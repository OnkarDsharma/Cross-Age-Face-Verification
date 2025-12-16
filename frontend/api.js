// api.js
const API_URL = 'http://localhost:5000';

export async function verifyFaces(image1File, image2File) {
    const formData = new FormData();
    formData.append('image1', image1File);
    formData.append('image2', image2File);
    
    try {
        const response = await fetch(`${API_URL}/predict`, {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Prediction failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

export async function checkHealth() {
    const response = await fetch(`${API_URL}/health`);
    return await response.json();
}

export async function getModelInfo() {
    const response = await fetch(`${API_URL}/model-info`);
    return await response.json();
}