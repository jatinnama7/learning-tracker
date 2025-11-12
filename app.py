"""
Personal Learning Tracker & Knowledge Graph Builder - Streamlit UI
A beautiful and intuitive web interface for tracking learning resources
"""

import streamlit as st
import json
import os
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Set
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
from learning_tracker import LearningTracker

# Page configuration
st.set_page_config(
    page_title="Learning Tracker",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with dark mode support
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    /* Dark mode support for sub-header - multiple detection methods */
    @media (prefers-color-scheme: dark) {
        .sub-header {
            color: #e0e0e0 !important;
        }
    }
    /* Streamlit dark mode detection */
    [data-theme="dark"] .sub-header,
    .stApp[data-theme="dark"] .sub-header,
    section[data-testid="stAppViewContainer"]:has([data-theme="dark"]) .sub-header {
        color: #e0e0e0 !important;
    }
    /* Additional Streamlit dark mode selectors */
    .stApp[data-theme="dark"] .sub-header {
        color: #e0e0e0 !important;
    }
    .resource-card {
        background-color: var(--background-color, #f8f9fa);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    [data-theme="dark"] .resource-card {
        background-color: #1e1e1e;
        border-left-color: #4a9eff;
    }
    .stat-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }
    .concept-tag {
        display: inline-block;
        background-color: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        margin: 0.2rem;
        font-size: 0.9rem;
    }
    [data-theme="dark"] .concept-tag {
        background-color: #1e3a5f;
        color: #64b5f6;
    }
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    .status-in_progress {
        background-color: #fff3cd;
        color: #856404;
    }
    [data-theme="dark"] .status-in_progress {
        background-color: #664d03;
        color: #ffc107;
    }
    .status-completed {
        background-color: #d4edda;
        color: #155724;
    }
    [data-theme="dark"] .status-completed {
        background-color: #0f5132;
        color: #75b798;
    }
    .status-archived {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    [data-theme="dark"] .status-archived {
        background-color: #055160;
        color: #6edff6;
    }
    </style>
    <script>
    // Detect Streamlit theme and apply appropriate colors
    function updateThemeColors() {
        const isDark = document.querySelector('[data-theme="dark"]') || 
                      document.querySelector('.stApp[data-theme="dark"]') ||
                      window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        const subHeaders = document.querySelectorAll('.sub-header');
        subHeaders.forEach(header => {
            if (isDark) {
                header.style.color = '#e0e0e0';
            } else {
                header.style.color = '#2c3e50';
            }
        });
    }
    
    // Run on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', updateThemeColors);
    } else {
        updateThemeColors();
    }
    
    // Watch for theme changes
    const observer = new MutationObserver(updateThemeColors);
    observer.observe(document.body, { attributes: true, attributeFilter: ['data-theme'] });
    </script>
""", unsafe_allow_html=True)

# Initialize session state
if 'tracker' not in st.session_state:
    st.session_state.tracker = LearningTracker()
if 'refresh' not in st.session_state:
    st.session_state.refresh = False

def get_status_color(status):
    """Get color for status badge"""
    colors = {
        'in_progress': '#ffc107',
        'completed': '#28a745',
        'archived': '#17a2b8'
    }
    return colors.get(status, '#6c757d')

def get_type_icon(resource_type):
    """Get icon for resource type"""
    icons = {
        'article': '📄',
        'video': '🎥',
        'course': '🎓',
        'book': '📖',
        'tutorial': '📝',
        'podcast': '🎙️'
    }
    return icons.get(resource_type.lower(), '📚')

def create_knowledge_graph_visualization(tracker):
    """Create interactive knowledge graph visualization"""
    graph = tracker.build_knowledge_graph()
    
    if not graph:
        return None
    
    # Create NetworkX graph
    G = nx.Graph()
    for concept, connections in graph.items():
        for connection in connections:
            G.add_edge(concept, connection)
    
    if len(G.nodes()) == 0:
        return None
    
    # Use spring layout for positioning
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Extract node and edge positions
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    # Create edge trace
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="middle center",
        hoverinfo='text',
        marker=dict(
            size=30,
            color='#1f77b4',
            line=dict(width=2, color='white')
        )
    )
    
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        title=dict(
                            text='Knowledge Graph - Concept Connections',
                            font=dict(size=16)
                        ),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20,l=5,r=5,t=40),
                        annotations=[ dict(
                            text="Concepts that appear together in resources are connected",
                            showarrow=False,
                            xref="paper", yref="paper",
                            x=0.005, y=-0.002,
                            xanchor='left', yanchor='bottom',
                            font=dict(color="#888", size=12)
                        )],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        plot_bgcolor='white'
                    ))
    
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">📚 Personal Learning Tracker</div>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-bottom: 2rem;">Track your learning journey and visualize knowledge connections</p>', unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a page",
        ["🏠 Dashboard", "➕ Add Resource", "📋 View Resources", "🔍 Search", "📊 Knowledge Graph", "📈 Statistics"]
    )
    
    # Dashboard
    if page == "🏠 Dashboard":
        st.markdown('<div class="sub-header">Dashboard Overview</div>', unsafe_allow_html=True)
        
        stats = st.session_state.tracker.get_statistics()
        
        # Statistics cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
                <div class="stat-box">
                    <h3>{stats['total_resources']}</h3>
                    <p>Total Resources</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="stat-box">
                    <h3>{stats['unique_concepts']}</h3>
                    <p>Unique Concepts</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="stat-box">
                    <h3>{stats['unique_tags']}</h3>
                    <p>Unique Tags</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            completed = stats['by_status'].get('completed', 0)
            total = stats['total_resources']
            completion_rate = (completed / total * 100) if total > 0 else 0
            st.markdown(f"""
                <div class="stat-box">
                    <h3>{completion_rate:.1f}%</h3>
                    <p>Completion Rate</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Recent resources
        st.markdown('<div class="sub-header">Recent Resources</div>', unsafe_allow_html=True)
        resources = st.session_state.tracker.list_resources()
        if resources:
            # Sort by date (most recent first)
            sorted_resources = sorted(resources, key=lambda x: x.get('date_added', ''), reverse=True)[:5]
            
            for resource in sorted_resources:
                status = resource.get('status', 'in_progress')
                resource_type = resource.get('type', 'article')
                icon = get_type_icon(resource_type)
                
                # Use Streamlit container for better styling
                with st.container():
                    st.markdown(f"""
                        <div class="resource-card">
                            <h4>{icon} {resource['title']}</h4>
                            <p><strong>Type:</strong> {resource_type.title()} | 
                            <strong>Status:</strong> <span class="status-badge status-{status}">{status.replace('_', ' ').title()}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Display details using Streamlit components
                    col1, col2 = st.columns(2)
                    with col1:
                        if resource.get('url'):
                            st.markdown(f"**URL:** [{resource['url']}]({resource['url']})")
                        if resource.get('tags'):
                            tags_str = ', '.join(resource.get('tags', []))
                            st.markdown(f"**Tags:** {tags_str}")
                    with col2:
                        if resource.get('concepts'):
                            concepts_str = ', '.join(resource.get('concepts', []))
                            st.markdown(f"**Concepts:** {concepts_str}")
                        st.markdown(f"**Added:** {resource.get('date_added', 'N/A')}")
                    
                    if resource.get('notes'):
                        st.info(f"**Notes:** {resource.get('notes', '')}")
                    
                    st.markdown("---")  # Divider between resources
        else:
            st.info("No resources yet. Add your first resource using the 'Add Resource' page!")
        
        # Quick stats charts
        if stats['total_resources'] > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="sub-header">Resources by Status</div>', unsafe_allow_html=True)
                status_data = stats['by_status']
                if status_data:
                    fig_status = px.pie(
                        values=list(status_data.values()),
                        names=list(status_data.keys()),
                        title="Status Distribution",
                        color_discrete_map={
                            'in_progress': '#ffc107',
                            'completed': '#28a745',
                            'archived': '#17a2b8'
                        }
                    )
                    st.plotly_chart(fig_status, use_container_width=True)
            
            with col2:
                st.markdown('<div class="sub-header">Resources by Type</div>', unsafe_allow_html=True)
                type_data = stats['by_type']
                if type_data:
                    fig_type = px.bar(
                        x=list(type_data.keys()),
                        y=list(type_data.values()),
                        title="Resources by Type",
                        labels={'x': 'Type', 'y': 'Count'}
                    )
                    fig_type.update_traces(marker_color='#1f77b4')
                    st.plotly_chart(fig_type, use_container_width=True)
    
    # Add Resource
    elif page == "➕ Add Resource":
        st.markdown('<div class="sub-header">Add New Learning Resource</div>', unsafe_allow_html=True)
        
        with st.form("add_resource_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                title = st.text_input("Title *", placeholder="e.g., Python Decorators Explained")
                resource_type = st.selectbox(
                    "Resource Type *",
                    ["article", "video", "course", "book", "tutorial", "podcast", "other"]
                )
                url = st.text_input("URL", placeholder="https://example.com/resource")
            
            with col2:
                tags_input = st.text_input("Tags (comma-separated)", placeholder="python, advanced, functions")
                concepts_input = st.text_input("Key Concepts (comma-separated)", placeholder="decorators, closures, first-class functions")
                status = st.selectbox("Status", ["in_progress", "completed", "archived"])
            
            notes = st.text_area("Notes", placeholder="Add any additional notes about this resource...", height=100)
            
            submitted = st.form_submit_button("➕ Add Resource", use_container_width=True)
            
            if submitted:
                if title:
                    tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
                    concepts = [c.strip() for c in concepts_input.split(",") if c.strip()] if concepts_input else []
                    
                    st.session_state.tracker.add_resource(
                        title=title,
                        resource_type=resource_type,
                        url=url,
                        tags=tags,
                        notes=notes,
                        concepts=concepts
                    )
                    st.session_state.tracker.update_status(
                        len(st.session_state.tracker.resources),
                        status
                    )
                    
                    st.success(f"✅ Successfully added: {title}")
                    st.balloons()
                else:
                    st.error("Please provide a title for the resource.")
    
    # View Resources
    elif page == "📋 View Resources":
        st.markdown('<div class="sub-header">All Learning Resources</div>', unsafe_allow_html=True)
        
        resources = st.session_state.tracker.list_resources()
        
        if resources:
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.selectbox(
                    "Filter by Status",
                    ["All", "in_progress", "completed", "archived"]
                )
            
            with col2:
                all_types = ["All"] + list(set([r.get('type', 'unknown') for r in resources]))
                type_filter = st.selectbox("Filter by Type", all_types)
            
            with col3:
                all_tags = ["All"] + sorted(set([tag for r in resources for tag in r.get('tags', [])]))
                tag_filter = st.selectbox("Filter by Tag", all_tags)
            
            # Apply filters
            filtered_resources = resources
            if status_filter != "All":
                filtered_resources = [r for r in filtered_resources if r.get('status') == status_filter]
            if type_filter != "All":
                filtered_resources = [r for r in filtered_resources if r.get('type') == type_filter]
            if tag_filter != "All":
                filtered_resources = [r for r in filtered_resources if tag_filter.lower() in [t.lower() for t in r.get('tags', [])]]
            
            st.info(f"Showing {len(filtered_resources)} of {len(resources)} resources")
            
            # Display resources
            for resource in filtered_resources:
                status = resource.get('status', 'in_progress')
                resource_type = resource.get('type', 'article')
                icon = get_type_icon(resource_type)
                
                with st.expander(f"{icon} {resource['title']} (ID: {resource['id']})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Type:** {resource_type.title()}")
                        st.write(f"**Status:** {status.replace('_', ' ').title()}")
                        if resource.get('url'):
                            st.write(f"**URL:** [{resource['url']}]({resource['url']})")
                    
                    with col2:
                        st.write(f"**Date Added:** {resource.get('date_added', 'N/A')}")
                        if resource.get('tags'):
                            st.write(f"**Tags:** {', '.join(resource['tags'])}")
                    
                    if resource.get('concepts'):
                        st.write("**Concepts:**")
                        concepts_html = " ".join([f'<span class="concept-tag">{c}</span>' for c in resource['concepts']])
                        st.markdown(concepts_html, unsafe_allow_html=True)
                    
                    if resource.get('notes'):
                        st.write("**Notes:**")
                        st.info(resource['notes'])
                    
                    # Update status
                    new_status = st.selectbox(
                        f"Update Status (Resource {resource['id']})",
                        ["in_progress", "completed", "archived"],
                        index=["in_progress", "completed", "archived"].index(status),
                        key=f"status_{resource['id']}"
                    )
                    
                    if new_status != status:
                        if st.button(f"Update Status", key=f"update_{resource['id']}"):
                            st.session_state.tracker.update_status(resource['id'], new_status)
                            st.success(f"Status updated to {new_status}")
                            st.rerun()
        else:
            st.info("No resources found. Add your first resource using the 'Add Resource' page!")
    
    # Search
    elif page == "🔍 Search":
        st.markdown('<div class="sub-header">Search Resources</div>', unsafe_allow_html=True)
        
        search_query = st.text_input("Search", placeholder="Search by title, tags, concepts, or notes...")
        
        if search_query:
            results = st.session_state.tracker.search(search_query)
            
            if results:
                st.success(f"Found {len(results)} result(s)")
                
                for resource in results:
                    status = resource.get('status', 'in_progress')
                    resource_type = resource.get('type', 'article')
                    icon = get_type_icon(resource_type)
                    
                    # Use Streamlit container for better styling
                    with st.container():
                        st.markdown(f"""
                            <div class="resource-card">
                                <h4>{icon} {resource['title']}</h4>
                                <p><strong>Type:</strong> {resource_type.title()} | 
                                <strong>Status:</strong> <span class="status-badge status-{status}">{status.replace('_', ' ').title()}</span></p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Display details using Streamlit components
                        col1, col2 = st.columns(2)
                        with col1:
                            if resource.get('url'):
                                st.markdown(f"**URL:** [{resource['url']}]({resource['url']})")
                            if resource.get('tags'):
                                tags_str = ', '.join(resource.get('tags', []))
                                st.markdown(f"**Tags:** {tags_str}")
                        with col2:
                            if resource.get('concepts'):
                                concepts_str = ', '.join(resource.get('concepts', []))
                                st.markdown(f"**Concepts:** {concepts_str}")
                        
                        if resource.get('notes'):
                            st.info(f"**Notes:** {resource.get('notes', '')}")
                        
                        st.markdown("---")  # Divider between resources
            else:
                st.warning("No results found. Try a different search query.")
        else:
            st.info("Enter a search query to find resources.")
    
    # Knowledge Graph
    elif page == "📊 Knowledge Graph":
        st.markdown('<div class="sub-header">Knowledge Graph Visualization</div>', unsafe_allow_html=True)
        
        graph = st.session_state.tracker.build_knowledge_graph()
        
        if graph:
            st.info("This graph shows how concepts are connected based on resources where they appear together.")
            
            # Interactive graph visualization
            fig = create_knowledge_graph_visualization(st.session_state.tracker)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            
            # Concept selector
            st.markdown("### Explore Concept Connections")
            all_concepts = sorted(set([c for r in st.session_state.tracker.resources for c in r.get('concepts', [])]))
            
            if all_concepts:
                selected_concept = st.selectbox("Select a concept to view its connections", ["All"] + all_concepts)
                
                if selected_concept != "All":
                    related = st.session_state.tracker.get_related_concepts(selected_concept)
                    if related:
                        st.success(f"Found {len(related)} related concept(s) for '{selected_concept}':")
                        concepts_html = " ".join([f'<span class="concept-tag">{c}</span>' for c in sorted(related)])
                        st.markdown(concepts_html, unsafe_allow_html=True)
                        
                        # Show resources containing this concept
                        st.markdown("### Resources containing this concept:")
                        concept_resources = [r for r in st.session_state.tracker.resources if selected_concept in r.get('concepts', [])]
                        for resource in concept_resources:
                            st.write(f"• **{resource['title']}** ({resource.get('type', 'unknown')})")
                    else:
                        st.info(f"No connections found for '{selected_concept}' yet.")
                else:
                    # Show all connections
                    st.markdown("### All Concept Connections")
                    for concept, connections in sorted(graph.items()):
                        if connections:
                            with st.expander(f"📌 {concept} ({len(connections)} connections)"):
                                concepts_html = " ".join([f'<span class="concept-tag">{c}</span>' for c in sorted(connections)])
                                st.markdown(concepts_html, unsafe_allow_html=True)
            else:
                st.info("No concepts found. Add resources with concepts to build the knowledge graph!")
        else:
            st.warning("No knowledge graph data available. Add resources with concepts to build connections!")
    
    # Statistics
    elif page == "📈 Statistics":
        st.markdown('<div class="sub-header">Learning Statistics</div>', unsafe_allow_html=True)
        
        stats = st.session_state.tracker.get_statistics()
        
        if stats['total_resources'] > 0:
            # Key metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Resources", stats['total_resources'])
            
            with col2:
                st.metric("Unique Concepts", stats['unique_concepts'])
            
            with col3:
                st.metric("Unique Tags", stats['unique_tags'])
            
            # Status distribution
            st.markdown("### Status Distribution")
            status_data = stats['by_status']
            if status_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_status = px.pie(
                        values=list(status_data.values()),
                        names=list(status_data.keys()),
                        title="Resources by Status",
                        color_discrete_map={
                            'in_progress': '#ffc107',
                            'completed': '#28a745',
                            'archived': '#17a2b8'
                        }
                    )
                    st.plotly_chart(fig_status, use_container_width=True)
                
                with col2:
                    status_df = {'Status': list(status_data.keys()), 'Count': list(status_data.values())}
                    st.dataframe(status_df, use_container_width=True, hide_index=True)
            
            # Type distribution
            st.markdown("### Type Distribution")
            type_data = stats['by_type']
            if type_data:
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_type = px.bar(
                        x=list(type_data.keys()),
                        y=list(type_data.values()),
                        title="Resources by Type",
                        labels={'x': 'Type', 'y': 'Count'},
                        color=list(type_data.values()),
                        color_continuous_scale='Blues'
                    )
                    st.plotly_chart(fig_type, use_container_width=True)
                
                with col2:
                    type_df = {'Type': list(type_data.keys()), 'Count': list(type_data.values())}
                    st.dataframe(type_df, use_container_width=True, hide_index=True)
            
            # All concepts and tags
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### All Concepts")
                all_concepts = sorted(set([c for r in st.session_state.tracker.resources for c in r.get('concepts', [])]))
                if all_concepts:
                    concepts_html = " ".join([f'<span class="concept-tag">{c}</span>' for c in all_concepts])
                    st.markdown(concepts_html, unsafe_allow_html=True)
                else:
                    st.info("No concepts added yet.")
            
            with col2:
                st.markdown("### All Tags")
                all_tags = sorted(set([tag for r in st.session_state.tracker.resources for tag in r.get('tags', [])]))
                if all_tags:
                    tags_html = " ".join([f'<span class="concept-tag">{tag}</span>' for tag in all_tags])
                    st.markdown(tags_html, unsafe_allow_html=True)
                else:
                    st.info("No tags added yet.")
        else:
            st.info("No statistics available. Add resources to see your learning progress!")

if __name__ == "__main__":
    main()

