import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink, Calendar, Tag } from 'lucide-react';
import moment from 'moment';
import './VideoModal.css';

const VideoModal = ({ item, onClose }) => {
    if (!item) return null;

    const getEmbedUrl = (url) => {
        if (!url) return null;
        if (url.includes('instagram.com/reel/') || url.includes('instagram.com/p/')) {
            const cleanUrl = url.split('?')[0];
            return `${cleanUrl}embed`;
        }
        if (url.includes('youtube.com/watch?v=')) {
            const videoId = url.split('v=')[1]?.split('&')[0];
            return `https://www.youtube.com/embed/${videoId}?autoplay=1`;
        }
        if (url.includes('youtube.com/shorts/')) {
            const videoId = url.split('shorts/')[1]?.split('?')[0];
            return `https://www.youtube.com/embed/${videoId}?autoplay=1`;
        }
        if (url.includes('youtu.be/')) {
            const videoId = url.split('youtu.be/')[1]?.split('?')[0];
            return `https://www.youtube.com/embed/${videoId}?autoplay=1`;
        }
        return null;
    };

    const embedUrl = getEmbedUrl(item.url);

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="modal-overlay"
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    className="modal-content"
                    onClick={(e) => e.stopPropagation()}
                >
                    <button className="modal-close" onClick={onClose}>
                        <X size={24} />
                    </button>

                    <div className="modal-body">
                        <div className="video-section">
                            {embedUrl ? (
                                <iframe
                                    src={embedUrl}
                                    className="modal-video-player"
                                    frameBorder="0"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                ></iframe>
                            ) : (
                                <div className="no-video-placeholder">
                                    <p>Preview not available for this platform.</p>
                                    <a href={item.url} target="_blank" rel="noopener noreferrer" className="visit-link">
                                        Visit Original Post <ExternalLink size={16} />
                                    </a>
                                </div>
                            )}
                        </div>

                        <div className="info-section">
                            <div className="info-header">
                                <span className="modal-platform-badge">{item.item_type}</span>
                                <span className="modal-category-badge">{item.category}</span>
                            </div>

                            <h2 className="modal-title">{item.title || 'Untitled Save'}</h2>

                            <div className="modal-meta">
                                <span className="meta-item">
                                    <Calendar size={14} /> {moment(item.created_at).format('MMM Do, YYYY')}
                                </span>
                                <a href={item.url} target="_blank" rel="noopener noreferrer" className="meta-link">
                                    Original Link <ExternalLink size={14} />
                                </a>
                            </div>

                            <div className="modal-description">
                                <h3>Summary</h3>
                                <p>{item.summary || 'No summary available.'}</p>
                                {item.caption && (
                                    <>
                                        <h3>Original Caption</h3>
                                        <p className="caption-text">{item.caption}</p>
                                    </>
                                )}
                            </div>

                            {item.hashtags && item.hashtags.length > 0 && (
                                <div className="modal-tags">
                                    {item.hashtags.map((tag, i) => (
                                        <span key={i} className="modal-tag">
                                            <Tag size={12} /> {tag.replace('#', '')}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
};

export default VideoModal;
