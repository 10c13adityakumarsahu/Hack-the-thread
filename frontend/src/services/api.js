import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:8000/api/',
});

export const getItems = () => api.get('items/');
export const deleteItem = (id) => api.delete(`items/${id}/`);

export default api;
