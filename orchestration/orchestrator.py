"""
Orquestrador Universal - Arquitetura Medalhão
==============================================
Orquestrador genérico e reutilizável para qualquer área de negócio.

Uso:
    python orchestrator.py --area plantio --config config/plantio.yaml
"""

import sys
import yaml
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Adiciona utils ao path
sys.path.append(str(Path(__file__).parent.parent / "utils"))

from config_loader import get_config_loader
from logger import PipelineLogger


class Orchestrator:
    """
    Orquestrador universal para pipelines de dados.

    Este orquestrador pode executar qualquer combinação de notebooks
    nas camadas Bronze, Silver e Gold.
    """

    def __init__(self, area: str, config_file: str = None):
        """
        Inicializa o orquestrador.

        Args:
            area: Área de negócio (plantio, vinhaca, etc.)
            config_file: Arquivo YAML de configuração
        """
        self.area = area
        self.config_file = config_file or f"orchestration/config/{area}.yaml"

        # Carrega configurações
        self.global_config = get_config_loader()
        self.pipeline_config = self._load_pipeline_config()

        # Inicializa logger
        self.logger = PipelineLogger(
            pipeline_name=f"orchestrator_{area}",
            config=self.global_config.config
        )

        self.results = []

    def _load_pipeline_config(self) -> Dict:
        """Carrega configuração específica do pipeline."""
        config_path = Path(self.config_file)

        if not config_path.exists():
            raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def execute_notebook(
        self,
        notebook_path: str,
        layer: str,
        source: str,
        timeout: int = 3600,
        parameters: Dict = None
    ) -> Dict:
        """
        Executa um notebook.

        Args:
            notebook_path: Caminho do notebook
            layer: Camada (bronze, silver, gold)
            source: Nome da fonte/processo
            timeout: Timeout em segundos
            parameters: Parâmetros para o notebook

        Returns:
            Dicionário com resultado da execução
        """
        start_time = datetime.now()

        try:
            self.logger.info(f"▶️ Executando: {layer.upper()} - {source}")
            self.logger.info(f"   Notebook: {notebook_path}")

            # Databricks notebook execution
            try:
                import dbutils
                result = dbutils.notebook.run(
                    notebook_path,
                    timeout,
                    parameters or {}
                )
                status = "success"
                output = result

            except NameError:
                # dbutils não disponível (ambiente local/teste)
                self.logger.warning(f"⚠️ dbutils não disponível - simulando execução")
                status = "simulated"
                output = "Simulado - dbutils não disponível"

            except Exception as e:
                status = "failed"
                output = str(e)
                self.logger.error(f"❌ Erro em {notebook_path}", exception=e)

        except Exception as e:
            status = "failed"
            output = str(e)
            self.logger.error(f"❌ Erro ao executar {notebook_path}", exception=e)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        return {
            "layer": layer,
            "source": source,
            "notebook": notebook_path,
            "status": status,
            "output": output,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration
        }

    def execute_layer(self, layer: str) -> List[Dict]:
        """
        Executa todos os notebooks de uma camada.

        Args:
            layer: Nome da camada (bronze, silver, gold)

        Returns:
            Lista de resultados
        """
        layer_config = self.pipeline_config.get('layers', {}).get(layer, {})

        if not layer_config.get('enabled', True):
            self.logger.warning(f"⚠️ Camada {layer} desabilitada - pulando")
            return []

        notebooks = layer_config.get('notebooks', [])
        mode = layer_config.get('execution_mode', 'serial')

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"🥉 CAMADA {layer.upper()}")
        self.logger.info(f"   Notebooks: {len(notebooks)}")
        self.logger.info(f"   Modo: {mode}")
        self.logger.info(f"{'='*80}\n")

        results = []

        if mode == 'parallel':
            # Execução paralela
            max_workers = layer_config.get('max_parallel_workers', 3)

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self.execute_notebook,
                        nb['path'],
                        layer,
                        nb.get('name', nb['path']),
                        nb.get('timeout', 3600),
                        nb.get('parameters', {})
                    ): nb
                    for nb in notebooks
                }

                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)

        else:
            # Execução serial
            for nb in notebooks:
                result = self.execute_notebook(
                    nb['path'],
                    layer,
                    nb.get('name', nb['path']),
                    nb.get('timeout', 3600),
                    nb.get('parameters', {})
                )
                results.append(result)

                # Para em caso de erro se configurado
                if result['status'] == 'failed' and not layer_config.get('continue_on_error', False):
                    self.logger.error(f"❌ Parando execução devido a erro em {nb['path']}")
                    break

        return results

    def execute(self) -> Dict:
        """
        Executa o pipeline completo.

        Returns:
            Dicionário com resultados da execução
        """
        self.logger.start(
            area=self.area,
            pipeline=self.pipeline_config.get('name', 'Pipeline'),
            version=self.pipeline_config.get('version', '1.0')
        )

        try:
            # Ordem de execução das camadas
            layers_order = self.pipeline_config.get('execution_order', ['bronze', 'silver', 'gold'])

            all_results = []

            for layer in layers_order:
                layer_results = self.execute_layer(layer)
                all_results.extend(layer_results)

            # Análise de resultados
            total = len(all_results)
            success = sum(1 for r in all_results if r['status'] == 'success')
            failed = sum(1 for r in all_results if r['status'] == 'failed')
            simulated = sum(1 for r in all_results if r['status'] == 'simulated')

            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"📊 RESUMO DA EXECUÇÃO")
            self.logger.info(f"{'='*80}")
            self.logger.info(f"Total de notebooks: {total}")
            self.logger.info(f"✅ Sucesso: {success}")
            self.logger.info(f"❌ Falhas: {failed}")
            self.logger.info(f"⚠️ Simulados: {simulated}")
            self.logger.info(f"{'='*80}\n")

            # Determina status geral
            if failed == 0:
                status = "success"
            elif success > 0:
                status = "partial"
            else:
                status = "failed"

            self.logger.end(status=status)

            return {
                "pipeline": self.pipeline_config.get('name'),
                "area": self.area,
                "status": status,
                "total_notebooks": total,
                "success": success,
                "failed": failed,
                "simulated": simulated,
                "results": all_results,
                "summary": self.logger.get_execution_summary()
            }

        except Exception as e:
            self.logger.error("Erro crítico no orquestrador", exception=e)
            self.logger.end(status="failed")
            raise


def main():
    """Ponto de entrada principal."""
    parser = argparse.ArgumentParser(description="Orquestrador de Pipelines")

    parser.add_argument(
        "--area",
        required=True,
        help="Área de negócio (plantio, vinhaca, preparo_solo, etc.)"
    )

    parser.add_argument(
        "--config",
        help="Arquivo de configuração YAML (padrão: orchestration/config/{area}.yaml)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Execução simulada (apenas mostra o que seria executado)"
    )

    args = parser.parse_args()

    # Cria orquestrador
    orch = Orchestrator(area=args.area, config_file=args.config)

    if args.dry_run:
        print("\n🔍 DRY RUN - Mostrando configuração sem executar:\n")
        print(yaml.dump(orch.pipeline_config, default_flow_style=False, allow_unicode=True))
        return

    # Executa pipeline
    result = orch.execute()

    # Salva resultado em arquivo
    output_file = Path(f"orchestration/results/{args.area}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Resultado salvo em: {output_file}")

    # Retorna exit code baseado no status
    if result['status'] == 'success':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
