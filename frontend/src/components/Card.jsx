import React from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Tag, Clock, Trash2 } from 'lucide-react';
import moment from 'moment';
import './Card.css';

const Card = ({ item, onDelete }) => {
    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            whileHover={{ y: -5 }}
            className="glass card-container"
        >
            <div className="card-header">
                <span className="category-badge">
                    {item.category || 'General'}
                </span>
                <button
                    onClick={() => onDelete(item.id)}
                    className="delete-btn"
                >
                    <Trash2 size={18} />
                </button>
            </div>

            <div style={{ flex: 1 }}>
                <h3 className="card-title">{item.title || 'Untitled Save'}</h3>
                <p className="card-summary">
                    {item.summary || item.caption || 'No description available.'}
                </p>
            </div>

            <div className="tag-list">
                {item.hashtags?.map((tag, i) => (
                    <span key={i} className="tag-item">
                        <Tag size={10} style={{ marginRight: '4px' }} /> {tag.replace('#', '')}
                    </span>
                ))}
            </div>

            <div className="card-footer">
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <Clock size={14} style={{ marginRight: '4px' }} />
                    {moment(item.created_at).fromNow()}
                </div>
                <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="footer-link"
                >
                    View Source <ExternalLink size={14} style={{ marginLeft: '4px' }} />
                </a>
            </div>
        </motion.div>
    );
};

export default Card;
