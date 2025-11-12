"""
Personal Learning Tracker & Knowledge Graph Builder
A simple tool to track learning resources and visualize knowledge connections
"""

import json
import os
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Set


class LearningTracker:
    def __init__(self, db_file: str = "learning_db.json"):
        self.db_file = db_file
        self.resources = self._load_data()
    
    def _load_data(self) -> List[Dict]:
        """Load learning resources from JSON file"""
        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def _save_data(self):
        """Save learning resources to JSON file"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.resources, f, indent=2, ensure_ascii=False)
    
    def add_resource(self, title: str, resource_type: str, url: str = "", 
                     tags: List[str] = None, notes: str = "", concepts: List[str] = None):
        """Add a new learning resource"""
        if tags is None:
            tags = []
        if concepts is None:
            concepts = []
        
        resource = {
            "id": len(self.resources) + 1,
            "title": title,
            "type": resource_type,  # article, video, course, book, etc.
            "url": url,
            "tags": tags,
            "concepts": concepts,  # Key concepts learned
            "notes": notes,
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "in_progress"  # in_progress, completed, archived
        }
        
        self.resources.append(resource)
        self._save_data()
        print(f"✓ Added: {title}")
        return resource
    
    def list_resources(self, status: str = None, tag: str = None):
        """List all resources, optionally filtered by status or tag"""
        filtered = self.resources
        
        if status:
            filtered = [r for r in filtered if r.get("status") == status]
        
        if tag:
            filtered = [r for r in filtered if tag.lower() in [t.lower() for t in r.get("tags", [])]]
        
        return filtered
    
    def search(self, query: str):
        """Search resources by title, tags, concepts, or notes"""
        query_lower = query.lower()
        results = []
        
        for resource in self.resources:
            if (query_lower in resource["title"].lower() or
                query_lower in resource["notes"].lower() or
                any(query_lower in tag.lower() for tag in resource.get("tags", [])) or
                any(query_lower in concept.lower() for concept in resource.get("concepts", []))):
                results.append(resource)
        
        return results
    
    def update_status(self, resource_id: int, status: str):
        """Update the status of a resource"""
        for resource in self.resources:
            if resource["id"] == resource_id:
                resource["status"] = status
                self._save_data()
                print(f"✓ Updated {resource['title']} to {status}")
                return True
        print(f"✗ Resource ID {resource_id} not found")
        return False
    
    def build_knowledge_graph(self) -> Dict[str, Set[str]]:
        """Build a knowledge graph showing connections between concepts"""
        graph = defaultdict(set)
        
        # For each resource, connect all its concepts together
        for resource in self.resources:
            concepts = resource.get("concepts", [])
            # Create connections between all concepts in the same resource
            for i, concept1 in enumerate(concepts):
                for concept2 in concepts[i+1:]:
                    graph[concept1].add(concept2)
                    graph[concept2].add(concept1)
        
        return dict(graph)
    
    def get_related_concepts(self, concept: str) -> List[str]:
        """Get concepts related to a given concept"""
        graph = self.build_knowledge_graph()
        return list(graph.get(concept, []))
    
    def get_statistics(self) -> Dict:
        """Get statistics about learning progress"""
        total = len(self.resources)
        by_status = defaultdict(int)
        by_type = defaultdict(int)
        all_concepts = set()
        all_tags = set()
        
        for resource in self.resources:
            by_status[resource.get("status", "unknown")] += 1
            by_type[resource.get("type", "unknown")] += 1
            all_concepts.update(resource.get("concepts", []))
            all_tags.update(resource.get("tags", []))
        
        return {
            "total_resources": total,
            "by_status": dict(by_status),
            "by_type": dict(by_type),
            "unique_concepts": len(all_concepts),
            "unique_tags": len(all_tags)
        }
    
    def visualize_connections(self, concept: str = None):
        """Visualize knowledge connections (text-based)"""
        graph = self.build_knowledge_graph()
        
        if concept:
            # Show connections for a specific concept
            related = graph.get(concept, set())
            if related:
                print(f"\n📚 Connections for '{concept}':")
                for related_concept in sorted(related):
                    print(f"  • {related_concept}")
            else:
                print(f"No connections found for '{concept}'")
        else:
            # Show all connections
            print("\n📊 Knowledge Graph Connections:")
            for concept, connections in sorted(graph.items()):
                if connections:
                    print(f"\n{concept}:")
                    for conn in sorted(connections):
                        print(f"  └─ {conn}")
            
            if not graph:
                print("No connections found. Add resources with concepts to build the graph!")


def main():
    """CLI interface for the Learning Tracker"""
    tracker = LearningTracker()
    
    print("=" * 60)
    print("📚 Personal Learning Tracker & Knowledge Graph Builder")
    print("=" * 60)
    
    while True:
        print("\nOptions:")
        print("1. Add resource")
        print("2. List resources")
        print("3. Search resources")
        print("4. Update status")
        print("5. View knowledge graph")
        print("6. View statistics")
        print("7. Exit")
        
        choice = input("\nEnter choice (1-7): ").strip()
        
        if choice == "1":
            print("\n--- Add Learning Resource ---")
            title = input("Title: ").strip()
            resource_type = input("Type (article/video/course/book): ").strip() or "article"
            url = input("URL (optional): ").strip()
            tags_input = input("Tags (comma-separated): ").strip()
            tags = [t.strip() for t in tags_input.split(",") if t.strip()]
            concepts_input = input("Key concepts (comma-separated): ").strip()
            concepts = [c.strip() for c in concepts_input.split(",") if c.strip()]
            notes = input("Notes (optional): ").strip()
            
            tracker.add_resource(title, resource_type, url, tags, notes, concepts)
        
        elif choice == "2":
            print("\n--- Resources ---")
            status_filter = input("Filter by status (in_progress/completed/archived) or press Enter for all: ").strip()
            tag_filter = input("Filter by tag (or press Enter for all): ").strip()
            
            resources = tracker.list_resources(
                status=status_filter if status_filter else None,
                tag=tag_filter if tag_filter else None
            )
            
            if resources:
                for r in resources:
                    print(f"\n[{r['id']}] {r['title']} ({r['type']})")
                    print(f"    Status: {r['status']}")
                    if r.get('tags'):
                        print(f"    Tags: {', '.join(r['tags'])}")
                    if r.get('concepts'):
                        print(f"    Concepts: {', '.join(r['concepts'])}")
                    if r.get('url'):
                        print(f"    URL: {r['url']}")
                    print(f"    Added: {r['date_added']}")
            else:
                print("No resources found.")
        
        elif choice == "3":
            query = input("\nSearch query: ").strip()
            results = tracker.search(query)
            
            if results:
                print(f"\nFound {len(results)} result(s):")
                for r in results:
                    print(f"  [{r['id']}] {r['title']} ({r['type']})")
            else:
                print("No results found.")
        
        elif choice == "4":
            try:
                resource_id = int(input("\nResource ID: ").strip())
                status = input("New status (in_progress/completed/archived): ").strip()
                tracker.update_status(resource_id, status)
            except ValueError:
                print("Invalid resource ID")
        
        elif choice == "5":
            concept = input("\nEnter concept to view connections (or press Enter for all): ").strip()
            tracker.visualize_connections(concept if concept else None)
        
        elif choice == "6":
            stats = tracker.get_statistics()
            print("\n--- Statistics ---")
            print(f"Total Resources: {stats['total_resources']}")
            print(f"Unique Concepts: {stats['unique_concepts']}")
            print(f"Unique Tags: {stats['unique_tags']}")
            print(f"\nBy Status:")
            for status, count in stats['by_status'].items():
                print(f"  {status}: {count}")
            print(f"\nBy Type:")
            for rtype, count in stats['by_type'].items():
                print(f"  {rtype}: {count}")
        
        elif choice == "7":
            print("\n👋 Happy learning!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

