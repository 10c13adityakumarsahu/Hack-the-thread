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

    const filteredItems = items.filter(item =>
        item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.hashtags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="dashboard-wrapper">
            <header className="dashboard-header">
                <motion.h1
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="dashboard-title"
                >
                    Social Saver <Sparkles className="inline-block" size={32} style={{ verticalAlign: 'middle', marginLeft: '10px' }} />
                </motion.h1>
                <p className="dashboard-subtitle">Your personal AI-powered knowledge base from social links.</p>

                <div className="search-container">
                    <Search className="search-icon" size={20} />
                    <input
                        type="text"
                        placeholder="Search your saves... (e.g. Pasta, Fitness)"
                        className="search-input"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>

                <button
                    onClick={fetchItems}
                    className="glass"
                    style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.875rem',
                        color: '#94a3b8',
                        display: 'flex',
                        alignItems: 'center',
                        margin: '0 auto 2rem'
                    }}
                >
                    <RefreshCw size={14} className={refreshing ? 'animate-spin mr-2' : 'mr-2'} style={{ marginRight: '8px' }} />
                    Refresh
                </button>
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
