from django.core.management.base import BaseCommand

from apps.rag.rag_pipeline import HybridRAGPipeline


class Command(BaseCommand):
    help = 'Rebuild the FAISS index from active BharatKart knowledge-base articles.'

    def handle(self, *args, **options):
        pipeline = HybridRAGPipeline()
        pipeline.bulk_index_knowledge_base()
        self.stdout.write(
            self.style.SUCCESS('Knowledge base indexed successfully.')
        )
