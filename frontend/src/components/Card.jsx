import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Tag, Clock, Trash2, Play } from 'lucide-react';
import moment from 'moment';
import './Card.css';

const Card = ({ item, onDelete }) => {
    const embedUrl = useMemo(() => {
        const url = item.url;
        if (url.includes('instagram.com/reel/') || url.includes('instagram.com/p/')) {
            const cleanUrl = url.split('?')[0];
            return `${cleanUrl}embed`;
        }
        if (url.includes('youtube.com/watch?v=')) {
            const videoId = url.split('v=')[1]?.split('&')[0];
            return `https://www.youtube.com/embed/${videoId}`;
        }
        if (url.includes('youtube.com/shorts/')) {
            const videoId = url.split('shorts/')[1]?.split('?')[0];
            return `https://www.youtube.com/embed/${videoId}`;
        }
        if (url.includes('youtu.be/')) {
            const videoId = url.split('youtu.be/')[1]?.split('?')[0];
            return `https://www.youtube.com/embed/${videoId}`;
        }
        return null;
    }, [item.url]);

    return (
        <motion.div
            layout
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9 }}
            whileHover={{ y: -5 }}
            className="card-container"
        >
            <div className="card-header">
                <div className="card-badges">
                    <span className="platform-badge">{item.item_type}</span>
                    <span className="category-badge">{item.category || 'General'}</span>
                </div>
                <button
                    onClick={() => onDelete(item.id)}
                    className="delete-btn"
                    title="Delete item"
                >
                    <Trash2 size={16} />
                </button>
            </div>

            {embedUrl ? (
                <div className="player-placeholder">
                    <iframe
                        src={embedUrl}
                        width="100%"
                        height="100%"
                        frameBorder="0"
                        scrolling="no"
                        allowTransparency="true"
                        allow="encrypted-media"
                        style={{ borderRadius: '12px' }}
                    ></iframe>
                </div>
            ) : (item.item_type === 'instagram' || item.item_type === 'x') ? (
                <div className="player-placeholder">
                    <Play className="player-icon" size={40} />
                </div>
            ) : null}

            <div style={{ flex: 1 }}>
                <h3 className="card-title">{item.title || 'Untitled Save'}</h3>
                <p className="card-summary">
                    {item.summary || item.caption || 'No description available.'}
                </p>
            </div>

            <div className="tag-list">
                {item.hashtags?.map((tag, i) => (
                    <span key={i} className="tag-item">
                        <Tag size={10} style={{ marginRight: '6px' }} /> {tag.replace('#', '')}
                    </span>
                ))}
            </div>

            <div className="card-footer">
                <div style={{ display: 'flex', alignItems: 'center' }}>
                    <Clock size={14} style={{ marginRight: '6px' }} />
                    {moment(item.created_at).fromNow()}
                </div>
                <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="footer-link"
                >
                    Source <ExternalLink size={14} style={{ marginLeft: '6px' }} />
                </a>
            </div>
        </motion.div>
    );
};

export default Card;
