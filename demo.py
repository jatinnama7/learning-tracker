"""
Quick demo script to show the Learning Tracker in action
Run this to see example data and features
"""

from learning_tracker import LearningTracker

def demo():
    print("=" * 60)
    print("🚀 Learning Tracker Demo")
    print("=" * 60)
    
    # Create tracker (will use demo_db.json to avoid overwriting your data)
    tracker = LearningTracker("demo_db.json")
    
    # Add some sample resources
    print("\n📝 Adding sample resources...\n")
    
    tracker.add_resource(
        title="Python Decorators Explained",
        resource_type="article",
        url="https://example.com/decorators",
        tags=["python", "advanced", "functions"],
        concepts=["decorators", "closures", "first-class functions"],
        notes="Great explanation of how decorators work"
    )
    
    tracker.add_resource(
        title="Async Programming in Python",
        resource_type="video",
        url="https://example.com/async",
        tags=["python", "async", "concurrency"],
        concepts=["async/await", "coroutines", "event loops"],
        notes="Comprehensive tutorial on async programming"
    )
    
    tracker.add_resource(
        title="Understanding Closures",
        resource_type="article",
        url="https://example.com/closures",
        tags=["python", "functions", "advanced"],
        concepts=["closures", "scope", "first-class functions"],
        notes="Deep dive into closure mechanics"
    )
    
    tracker.add_resource(
        title="Event Loop Architecture",
        resource_type="course",
        url="https://example.com/eventloop",
        tags=["python", "async", "architecture"],
        concepts=["event loops", "coroutines", "concurrency"],
        notes="Advanced course on event loop internals"
    )
    
    # Show statistics
    print("\n" + "=" * 60)
    print("📊 Statistics")
    print("=" * 60)
    stats = tracker.get_statistics()
    print(f"Total Resources: {stats['total_resources']}")
    print(f"Unique Concepts: {stats['unique_concepts']}")
    print(f"Unique Tags: {stats['unique_tags']}")
    print(f"\nBy Status: {stats['by_status']}")
    print(f"By Type: {stats['by_type']}")
    
    # Show knowledge graph
    print("\n" + "=" * 60)
    print("📚 Knowledge Graph")
    print("=" * 60)
    tracker.visualize_connections()
    
    # Show connections for a specific concept
    print("\n" + "=" * 60)
    print("🔗 Related Concepts for 'coroutines'")
    print("=" * 60)
    related = tracker.get_related_concepts("coroutines")
    for concept in related:
        print(f"  • {concept}")
    
    # Search example
    print("\n" + "=" * 60)
    print("🔍 Search Results for 'async'")
    print("=" * 60)
    results = tracker.search("async")
    for r in results:
        print(f"  [{r['id']}] {r['title']} ({r['type']})")
    
    print("\n" + "=" * 60)
    print("✅ Demo complete! Check demo_db.json to see the data.")
    print("=" * 60)
    print("\n💡 Tip: Run 'python learning_tracker.py' to use the interactive CLI!")

if __name__ == "__main__":
    demo()

