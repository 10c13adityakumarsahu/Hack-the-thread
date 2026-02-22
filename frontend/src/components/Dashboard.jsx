import React, { useState, useEffect } from 'react';
import { getItems, deleteItem, updateItem } from '../services/api';
import Card from './Card';
import VideoModal from './VideoModal';
import { Search, Loader2, RefreshCw, Menu, X, Filter, BarChart2, Calendar, Globe, Clock as ClockIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import moment from 'moment';
import './Dashboard.css';

const Dashboard = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [refreshing, setRefreshing] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState('All');
    const [selectedPlatform, setSelectedPlatform] = useState('All');
    const [selectedTimeRange, setSelectedTimeRange] = useState('All Time');
    const [sortBy, setSortBy] = useState('Newest');
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 1024);
    const [selectedItemForModal, setSelectedItemForModal] = useState(null);

    const categories = ['All', ...new Set(items.map(item => item.category).filter(Boolean))];
    const platforms = ['All', 'instagram', 'x', 'youtube', 'blog', 'other'];
    const timeRanges = ['All Time', 'Today', 'This Week', 'This Month'];

    useEffect(() => {
        const handleResize = () => {
            const mobile = window.innerWidth <= 1024;
            setIsMobile(mobile);
            if (!mobile) setSidebarOpen(false);
        };

        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

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

    const handleMarkAsSeen = async (item) => {
        if (!item.is_seen) {
            try {
                await updateItem(item.id, { is_seen: true });
                setItems(items.map(i => i.id === item.id ? { ...i, is_seen: true } : i));
            } catch (error) {
                console.error("Error marking item as seen:", error);
            }
        }
        setSelectedItemForModal(item);
    };

    const filteredItems = items
        .filter(item => {
            const matchesSearch =
                item.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.summary?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.category?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                item.hashtags?.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));

            const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
            const matchesPlatform = selectedPlatform === 'All' || item.item_type === selectedPlatform;

            let matchesTime = true;
            if (selectedTimeRange !== 'All Time') {
                const itemDate = moment(item.created_at);
                if (selectedTimeRange === 'Today') {
                    matchesTime = itemDate.isSame(moment(), 'day');
                } else if (selectedTimeRange === 'This Week') {
                    matchesTime = itemDate.isAfter(moment().subtract(7, 'days'));
                } else if (selectedTimeRange === 'This Month') {
                    matchesTime = itemDate.isAfter(moment().subtract(1, 'month'));
                }
            }

            return matchesSearch && matchesCategory && matchesPlatform && matchesTime;
        })
        .sort((a, b) => {
            if (sortBy === 'Newest') return new Date(b.created_at) - new Date(a.created_at);
            if (sortBy === 'Oldest') return new Date(a.created_at) - new Date(b.created_at);
            if (sortBy === 'Alpha') return (a.title || '').localeCompare(b.title || '');
            return 0;
        });

    const FilterGroups = ({ vertical = false }) => (
        <div className={vertical ? "filter-groups-vertical" : "filter-groups-horizontal"}>
            <div className="filter-group">
                <label><Globe size={14} /> Platform</label>
                <div className="filter-chips">
                    {platforms.map(p => (
                        <button
                            key={p}
                            className={`chip ${selectedPlatform === p ? 'active' : ''}`}
                            onClick={() => setSelectedPlatform(p)}
                        >
                            {p === 'x' ? 'X' : p.charAt(0).toUpperCase() + p.slice(1)}
                        </button>
                    ))}
                </div>
            </div>

            <div className="filter-group">
                <label><ClockIcon size={14} /> Time</label>
                <div className="filter-chips">
                    {timeRanges.map(t => (
                        <button
                            key={t}
                            className={`chip ${selectedTimeRange === t ? 'active' : ''}`}
                            onClick={() => setSelectedTimeRange(t)}
                        >
                            {t}
                        </button>
                    ))}
                </div>
            </div>

            <div className="filter-group">
                <label><Filter size={14} /> Category</label>
                <select
                    value={selectedCategory}
                    onChange={(e) => setSelectedCategory(e.target.value)}
                    className="filter-select"
                >
                    {categories.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
            </div>

            <div className="filter-group">
                <label><BarChart2 size={14} /> Sort</label>
                <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="filter-select"
                >
                    <option value="Newest">Newest First</option>
                    <option value="Oldest">Oldest First</option>
                    <option value="Alpha">A-Z</option>
                </select>
            </div>
        </div>
    );

    return (
        <div className="dashboard-container">
            <AnimatePresence>
                {isMobile && sidebarOpen && (
                    <>
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setSidebarOpen(false)}
                            className="sidebar-backdrop"
                        />
                        <motion.aside
                            initial={{ x: '-100%' }}
                            animate={{ x: 0 }}
                            exit={{ x: '-100%' }}
                            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                            className="mobile-sidebar"
                        >
                            <div className="sidebar-header">
                                <h2 className="brand-name">Filters</h2>
                                <button onClick={() => setSidebarOpen(false)}><X size={24} /></button>
                            </div>
                            <div className="sidebar-content">
                                <FilterGroups vertical />
                                <button onClick={fetchItems} className="refresh-btn-full">
                                    <RefreshCw size={16} className={refreshing ? 'animate-spin' : ''} />
                                    Refresh Collection
                                </button>
                            </div>
                        </motion.aside>
                    </>
                )}
            </AnimatePresence>

            <header className="top-nav">
                <div className="nav-main">
                    <div className="brand-section">
                        {isMobile && (
                            <button className="menu-trigger" onClick={() => setSidebarOpen(true)}>
                                <Menu size={24} />
                            </button>
                        )}
                        <h1 className="logo-text">Social<span>Saver</span></h1>
                    </div>

                    <div className="search-wrapper">
                        <Search size={18} className="search-icon" />
                        <input
                            type="text"
                            placeholder="Find something..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>

                    {!isMobile && (
                        <button onClick={fetchItems} className="refresh-icon-btn" title="Refresh">
                            <RefreshCw size={20} className={refreshing ? 'animate-spin' : ''} />
                        </button>
                    )}
                </div>

                {!isMobile && (
                    <div className="nav-filters">
                        <FilterGroups />
                    </div>
                )}
            </header>

            <main className="main-content">
                <div className="results-header">
                    <p className="results-count">Showing <span>{filteredItems.length}</span> items</p>
                </div>

                {loading ? (
                    <div className="loading-state">
                        <Loader2 className="spinner" size={40} />
                        <p>Curating your collection...</p>
                    </div>
                ) : (
                    <AnimatePresence mode="popLayout">
                        {filteredItems.length > 0 ? (
                            <motion.div layout className="items-grid">
                                {filteredItems.map(item => (
                                    <Card
                                        key={item.id}
                                        item={item}
                                        onDelete={handleDelete}
                                        onClick={() => handleMarkAsSeen(item)}
                                    />
                                ))}
                            </motion.div>
                        ) : (
                            <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="empty-state"
                            >
                                <div className="empty-icon">📂</div>
                                <h3>No items found</h3>
                                <p>Try adjusting your search or filters to find what you're looking for.</p>
                                <button className="reset-btn" onClick={() => {
                                    setSelectedCategory('All');
                                    setSelectedPlatform('All');
                                    setSelectedTimeRange('All Time');
                                    setSearchTerm('');
                                }}>Reset All Filters</button>
                            </motion.div>
                        )}
                    </AnimatePresence>
                )}
            </main>

            {selectedItemForModal && (
                <VideoModal
                    item={selectedItemForModal}
                    onClose={() => setSelectedItemForModal(null)}
                />
            )}
        </div>
    );
};

export default Dashboard;

