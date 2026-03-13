/**
 * Dyslexia Screening API Client
 * Works with your FastAPI service at /v1/*
 */

class DyslexiaClient {
    constructor(apiBaseUrl, apiKey) {
        this.apiBaseUrl = apiBaseUrl.replace(/\/+$/, ''); // remove trailing slash
        this.apiKey = apiKey;
    }

    _headers() {
        return {
            'X-API-Key': this.apiKey,
            'Content-Type': 'application/json'
        };
    }

    async analyzeSpeech(text, audioBlob) {
        const formData = new FormData();
        formData.append('text_file', new Blob([text], { type: 'text/plain' }), 'script.txt');
        formData.append('audio_file', audioBlob, 'recording.wav');

        const url = `${this.apiBaseUrl}/v1/speech-analyses?async=true`;
        console.log("url = " + url)
        const response = await fetch(url, {
            method: 'POST',
            headers: { 'X-API-Key': this.apiKey },
            body: formData
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Analyze failed: ${response.status} ${errorText}`);
        }

        const location = response.headers.get('Location');
        const body = await response.json();
        return {
            taskId: body.task_id,
            statusUrl: location ? `${this.apiBaseUrl}${location}` : null
        };
    }

    async getAnalysisResult(statusUrl) {
        const response = await fetch(statusUrl, {
            headers: { 'X-API-Key': this.apiKey }
        });
        if (response.status === 202) {
            return { status: 'processing' };
        }
        if (response.status === 200) {
            const result = await response.json();
            return { status: 'completed', result };
        }
        throw new Error(`Unexpected status: ${response.status}`);
    }

    async diagnose(analyses) {
        const url = `${this.apiBaseUrl}/v1/diagnostic-reports?async=true`;
        const response = await fetch(url, {
            method: 'POST',
            headers: this._headers(),
            body: JSON.stringify({ analyses })
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Diagnose failed: ${response.status} ${errorText}`);
        }

        const location = response.headers.get('Location');
        const body = await response.json();
        return {
            taskId: body.task_id,
            statusUrl: location ? `${this.apiBaseUrl}${location}` : null
        };
    }

    async getDiagnosisResult(statusUrl) {
        const response = await fetch(statusUrl, {
            headers: { 'X-API-Key': this.apiKey }
        });
        if (response.status === 202) {
            return { status: 'processing' };
        }
        if (response.status === 200) {
            const result = await response.json();
            return { status: 'completed', result };
        }
        throw new Error(`Unexpected status: ${response.status}`);
    }
}
