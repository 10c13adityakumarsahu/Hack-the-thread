import React, { useState, useEffect } from 'react';
import { getItems, deleteItem } from '../services/api';
import Card from './Card';
import { Search, Loader2, Sparkles, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import './Dashboard.css';

const Dashboard = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [refreshing, setRefreshing] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState('All');

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

    const filteredItems = items.filter(item => {
        const matchesSearch =
            item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.hashtags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

        const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;

        return matchesSearch && matchesCategory;
    });

    return (
        <div className="dashboard-wrapper">
            <header className="dashboard-header">
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="header-content"
                >
                    <h1 className="dashboard-title premium-gradient-text">
                        Social Saver <Sparkles className="inline-block" size={32} style={{ color: '#8b5cf6', marginLeft: '12px' }} />
                    </h1>
                    <p className="dashboard-subtitle">Curation of your digital brain. Powered by AI.</p>
                </motion.div>

                <div className="controls-row">
                    <div className="search-container glass">
                        <Search className="search-icon" size={20} />
                        <input
                            type="text"
                            placeholder="Find inspiration..."
                            className="search-input"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    <button
                        onClick={fetchItems}
                        className="refresh-btn glass glass-hover"
                    >
                        <RefreshCw size={18} className={refreshing ? 'animate-spin' : ''} />
                    </button>
                </div>

                <div className="category-filter">
                    {categories.map(cat => (
                        <button
                            key={cat}
                            onClick={() => setSelectedCategory(cat)}
                            className={`category-pill ${selectedCategory === cat ? 'active' : 'glass glass-hover'}`}
                        >
                            {cat}
                        </button>
                    ))}
                </div>
            </header>

            {loading ? (
                <div className="loading-container">
                    <Loader2 className="animate-spin mx-auto mb-4" size={48} />
                    <p>Loading your knowledge base...</p>
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
                            className="empty-container"
                        >
                            <p className="text-xl">No saves found. Send a link to your WhatsApp bot!</p>
                        </motion.div>
                    )}
                </AnimatePresence>
            )}
        </div>
    );
};

export default Dashboard;
