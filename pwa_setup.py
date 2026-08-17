import streamlit.components.v1 as components

def enable_pwa():
    """Injects PWA manifest and iOS meta tags to allow 'Add to Home Screen'"""
    
    # We use a data URI for the manifest so we don't need to host a static file
    manifest_json = """
    {
      "name": "College Notice Board",
      "short_name": "Notices",
      "start_url": ".",
      "display": "standalone",
      "background_color": "#FAFAFA",
      "theme_color": "#4285F4",
      "icons": [
        {
          "src": "https://cdn-icons-png.flaticon.com/512/3206/3206015.png",
          "sizes": "512x512",
          "type": "image/png",
          "purpose": "any maskable"
        }
      ]
    }
    """
    
    import json
    import base64
    
    # Convert manifest to base64
    b64_manifest = base64.b64encode(manifest_json.encode('utf-8')).decode('utf-8')
    manifest_url = f"data:application/manifest+json;base64,{b64_manifest}"
    
    # Inject into parent head
    components.html(f"""
    <script>
        const parentDoc = window.parent.document;
        
        // 1. Add Manifest for Android/Chrome
        if (!parentDoc.querySelector('link[rel="manifest"]')) {{
            const manifestLink = parentDoc.createElement('link');
            manifestLink.rel = 'manifest';
            manifestLink.href = '{manifest_url}';
            parentDoc.head.appendChild(manifestLink);
        }}
        
        // 2. Add iOS Meta tags
        const metaTags = [
            {{ name: 'apple-mobile-web-app-capable', content: 'yes' }},
            {{ name: 'apple-mobile-web-app-status-bar-style', content: 'black-translucent' }},
            {{ name: 'apple-mobile-web-app-title', content: 'Notices' }},
            {{ name: 'theme-color', content: '#4285F4' }}
        ];
        
        metaTags.forEach(tag => {{
            if (!parentDoc.querySelector(`meta[name="${{tag.name}}"]`)) {{
                const meta = parentDoc.createElement('meta');
                meta.name = tag.name;
                meta.content = tag.content;
                parentDoc.head.appendChild(meta);
            }}
        }});
        
        // 3. Add iOS Icon
        if (!parentDoc.querySelector('link[rel="apple-touch-icon"]')) {{
            const iconLink = parentDoc.createElement('link');
            iconLink.rel = 'apple-touch-icon';
            iconLink.href = 'https://cdn-icons-png.flaticon.com/512/3206/3206015.png';
            parentDoc.head.appendChild(iconLink);
        }}
    </script>
    """, height=0, width=0)
