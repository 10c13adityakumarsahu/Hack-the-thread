import React, { useState, useEffect } from 'react';
import { getItems, deleteItem } from '../services/api';
import Card from './Card';
import { Search, Loader2, RefreshCw, Menu, X, Filter, BarChart2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Dashboard.css';

const Dashboard = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [refreshing, setRefreshing] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [sortBy, setSortBy] = useState('Newest');
    const [sidebarOpen, setSidebarOpen] = useState(true);

    const categories = ['All', ...new Set(items.map(item => item.category).filter(Boolean))];

    const fetchItems = async () => {
        try {
            setRefreshing(true);
            const response = await getItems();
            setItems(response.data);
        } catch (error) {
            console.error("Error fetching items:", error);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    const handleDelete = async (id) => {
        try {
            await deleteItem(id);
            setItems(items.filter(item => item.id !== id));
        } catch (error) {
            console.error("Error deleting item:", error);
        }
    };

    const filteredItems = items
        .filter(item => {
            const matchesSearch =
                item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.hashtags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

            const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;

            return matchesSearch && matchesCategory;
        })
        .sort((a, b) => {
            if (sortBy === 'Newest') return new Date(b.created_at) - new Date(a.created_at);
            if (sortBy === 'Oldest') return new Date(a.created_at) - new Date(b.created_at);
            if (sortBy === 'Alpha') return a.title.localeCompare(b.title);
            return 0;
        });

    return (
        <div className="main-layout">
            <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
                <div className="sidebar-header">
                    <h2 className="brand-name">Social Saver</h2>
                    <button className="sidebar-close-btn" onClick={() => setSidebarOpen(false)}>
                        <X size={20} />
                    </button>
                </div>

                <div className="sidebar-section">
                    <h3 className="section-label">Categories</h3>
                    <div className="category-list">
                        {categories.map(cat => (
                            <button
                                key={cat}
                                onClick={() => setSelectedCategory(cat)}
                                className={`sidebar-item ${selectedCategory === cat ? 'active' : ''}`}
                            >
                                {cat}
                            </button>
                        ))}
                    </div>
                </div>

                <div className="sidebar-section">
                    <h3 className="section-label">Sort By</h3>
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value)}
                        className="sidebar-select"
                    >
                        <option value="Newest">Newest First</option>
                        <option value="Oldest">Oldest First</option>
                        <option value="Alpha">A-Z Order</option>
                    </select>
                </div>

                <div className="sidebar-footer">
                    <button onClick={fetchItems} className="refresh-sidebar-btn">
                        <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                        Sync Data
                    </button>
                </div>
            </aside>

            <main className="content-area">
                <header className="content-header">
                    {!sidebarOpen && (
                        <button className="menu-btn" onClick={() => setSidebarOpen(true)}>
                            <Menu size={24} />
                        </button>
                    )}

                    <div className="search-bar">
                        <Search size={18} className="search-icon" />
                        <input
                            type="text"
                            placeholder="Search collection..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </header>

                <div className="content-body">
                    {loading ? (
                        <div className="loader-box">
                            <Loader2 className="animate-spin" size={32} />
                            <p>Loading collection</p>
                        </div>
                    ) : (
                        <AnimatePresence mode="popLayout">
                            {filteredItems.length > 0 ? (
                                <motion.div
                                    layout
                                    className="items-grid"
                                >
                                    {filteredItems.map(item => (
                                        <Card key={item.id} item={item} onDelete={handleDelete} />
                                    ))}
                                </motion.div>
                            ) : (
                                <motion.div
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="empty-state"
                                >
                                    <p>No items found in this section.</p>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    )}
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
