import axios from 'axios';

const api = axios.create({
    baseURL: 'https://hack-the-thread.onrender.com/api/',
});

export const getItems = () => api.get('items/');
export const deleteItem = (id) => api.delete(`items/${id}/`);

export default api;
