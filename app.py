def chamar_gemini(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return "Erro: Chave API não configurada nos Secrets do Streamlit."
    
    # Ajuste: Usando a versão de modelo padrão suportada pela API v1
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Erro na API: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"
