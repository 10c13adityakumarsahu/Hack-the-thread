import axios from 'axios';

const api = axios.create({
    baseURL: 'https://hack-the-thread-zm6v.onrender.com/api/',
});

export const getItems = () => api.get('items/');
export const deleteItem = (id) => api.delete(`items/${id}/`);
export const updateItem = (id, data) => api.patch(`items/${id}/`, data);

export default api;
