import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Tag, Clock, Trash2, Play } from 'lucide-react';
import moment from 'moment';
import './Card.css';

const Card = ({ item, onDelete, onClick }) => {
    const isVideo = ['youtube', 'instagram', 'x'].includes(item.item_type);

    const getThumbnail = () => {
        if (item.item_type === 'youtube') {
            const videoId = item.url.split('v=')[1]?.split('&')[0] || item.url.split('shorts/')[1]?.split('?')[0] || item.url.split('youtu.be/')[1];
            if (videoId) return `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
        }
        return null; // Fallback to icon
    };

    const thumbnail = getThumbnail();

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            whileHover={{ y: -8, boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)' }}
            className={`card-container ${!item.is_seen ? 'is-new' : ''}`}
            onClick={onClick}
        >
            <div className="card-header">
                <div className="card-badges">
                    {!item.is_seen && <span className="new-badge">New</span>}
                    <span className="platform-badge">{item.item_type}</span>
                    <span className="category-badge">{item.category || 'General'}</span>
                </div>
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onDelete(item.id);
                    }}
                    className="delete-btn"
                    title="Delete item"
                >
                    <Trash2 size={16} />
                </button>
            </div>

            <div className="card-preview">
                {thumbnail ? (
                    <img src={thumbnail} alt={item.title} className="preview-img" />
                ) : (
                    <div className="preview-placeholder">
                        <Play className="play-icon" size={40} />
                    </div>
                )}
                {isVideo && (
                    <div className="play-overlay">
                        <Play size={48} fill="white" />
                    </div>
                )}
            </div>

            <div className="card-content">
                <h3 className="card-title">{item.title || 'Untitled Save'}</h3>
                <p className="card-summary">
                    {item.summary || item.caption || 'No description available.'}
                </p>

                <div className="tag-list">
                    {item.hashtags?.slice(0, 3).map((tag, i) => (
                        <span key={i} className="tag-item">
                            #{tag.replace('#', '')}
                        </span>
                    ))}
                    {item.hashtags?.length > 3 && (
                        <span className="tag-more">+{item.hashtags.length - 3}</span>
                    )}
                </div>
            </div>

            <div className="card-footer">
                <div className="footer-meta">
                    <Clock size={14} />
                    <span>{moment(item.created_at).fromNow()}</span>
                </div>
                <div className="footer-actions">
                    <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="source-link"
                        onClick={(e) => e.stopPropagation()}
                    >
                        Source <ExternalLink size={14} />
                    </a>
                </div>
            </div>
        </motion.div>
    );
};

export default Card;
