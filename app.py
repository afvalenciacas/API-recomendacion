from flask import Flask, render_template, request, jsonify, g
from flask_cors import CORS
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler
from scipy.sparse import csr_matrix

df = pd.read_csv("df_spotify.csv", sep='|')
df1 = df.copy()

def custom_recommendation_model(df, generos_usuario, seleccion_usuario, n_components, scaling_method, top_n):
    print(f'df de entrada: {df.head(10)}')
    print(f'Recomendaciones Modelo Entrando')
    subset_df = df[(df['genero_principal'].isin(generos_usuario)) & (df['sentimiento'] == seleccion_usuario)]
    if subset_df.shape[0] > 0:
        pass
    else: 
        subset_df = df[(df['genero_principal'].isin(generos_usuario)) | (df['sentimiento'] == seleccion_usuario)]

    atributos_deseados = ['valence', 'year', 'acousticness', 'danceability', 'energy', 'explicit',
                         'instrumentalness', 'key', 'liveness', 'loudness', 'mode', 'speechiness', 'tempo']
    
    atributos = subset_df[atributos_deseados].values
    
    # Aplicar el escalado
    if scaling_method == "StandardScaler":
        scaler = StandardScaler()
        atributos = scaler.fit_transform(atributos)
    elif scaling_method == "MinMaxScaler":
        scaler = MinMaxScaler()
        atributos = scaler.fit_transform(atributos)
    elif scaling_method == "RobustScaler":
        scaler = RobustScaler()
        atributos = scaler.fit_transform(atributos)
            
    print(f'Recomendaciones Modelo antes modelo')
    # Reducción de dimensionalidad (SVD)
    # n_components = min(n_components, min(atributos.shape) - 1)
    svd = TruncatedSVD(n_components=n_components)
    atributos_latentes = svd.fit_transform(atributos)

    print(f'Recomendaciones Modelo antes matriz dispersa')
    # Convertir a matriz dispersa
    atributos_latentes_sparse = csr_matrix(atributos_latentes)
    
    print(f'Recomendaciones Modelo antes similitud del coseno')
    # Calcular similitud del coseno
    similitud = cosine_similarity(atributos_latentes_sparse) if n_components < min(atributos.shape) else cosine_similarity(atributos)
    print(f'Recomendaciones Modelo despues similitud = ')
    indices_recomendaciones = similitud.sum(axis=0).argsort()[::-1]
    print(f'Recomendaciones Modelo despues indices_recomendaciones ')    
    print(f'Recomendaciones Modelo despues similitud coseno')

    recomendaciones = subset_df.iloc[indices_recomendaciones].head(10)
    print(f'Recomendaciones Modelo: {recomendaciones.head(10)}')

    return recomendaciones


app = Flask(__name__)
CORS(app)  # Esto permite solicitudes CORS desde cualquier origen

app.config['g_sentimiento'] = ""
app.config['g_generos'] = []
app.config['g_canciones_no_gustadas'] = []

#def before_request():
    #app.config['g_sentimiento'] = ""
    #app.config['g_generos'] = []
    #app.config['g_canciones_no_gustadas'] = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encuesta')
def encuesta():
    return render_template('encuesta.html', g_sentimiento=app.config['g_sentimiento'])

@app.route('/genero')
def genero():
    return render_template('genero.html', g_generos=app.config['g_generos'])

@app.route('/playlist')
def playlist():
    return render_template('playlist.html')

@app.route('/camweb')
def camweb():
    return render_template('camweb.html')

@app.route('/api/enviar-sentimiento', methods=['POST'])
def recibir_sentimiento():
    try:
        data = request.get_json()
        sentimiento = data.get('sentimiento')

        app.config['g_sentimiento'] = sentimiento

        # Imprimir el sentimiento en la consola del servidor Flask
        print(f'Sentimiento recibido: {sentimiento}')

        # Mensaje a mostrar en el navegador
        mensaje_navegador = f'El sentimiento elegido por el usuario es {sentimiento}'

        # Aquí puedes realizar acciones con el sentimiento recibido
        # En este ejemplo, simplemente lo devolvemos como parte de la respuesta
        return jsonify({'mensaje': f'Sentimiento: {sentimiento}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/enviar-generos', methods=['POST'])
def recibir_generos():
    try:
        data = request.get_json()
        generos = data.get('generos')
        app.config['g_generos'] = generos
        
        # Imprimir los géneros en la consola del servidor Flask
        print(f'Géneros recibidos: {generos}')

        # Puedes realizar acciones con los géneros recibidos aquí

        # En este ejemplo, simplemente lo devolvemos como parte de la respuesta
        return jsonify({'mensaje': f'Géneros recibidos: {generos}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generar-playlist', methods=['POST'])
def generar_playlist():
    try:
        data = request.get_json()
        # Aqui se hace la llamada del modelo que devuelve una play list segun sentimiento, generos
        
        sentimiento = app.config['g_sentimiento']
        generos = app.config['g_generos']

        print(f"Sentimiento: {sentimiento}")
        print(f"Géneros: {generos}")

        # Verificar si hay canciones no gustadas antes de aplicar el filtrado
        v_canciones_no_gustadas = app.config['g_canciones_no_gustadas']
        #print(f"v_canciones_no_gustadas: {v_canciones_no_gustadas}")
        #print(f"len v_canciones_no_gustadas: {len(v_canciones_no_gustadas)}")    

        if len(v_canciones_no_gustadas) == 0:
            df1 = df.copy()
            #print(f" df1 = df.copy()")
        else:
            df1 = df[~df['id'].isin(v_canciones_no_gustadas)]
            #print(f" Elimino Canciones no Gustadas")
 
        #playlist = "<ul><li>nombre_cancion_1 - Almara</li><li>nombre_cancion_2 - Alejandro Sanz</li></ul>"
        
        print(f" .... Generando Recomendaciones .... ")
        # Obtner Recomendaciones
        df_recomendaciones = custom_recommendation_model(df1, generos, sentimiento, n_components= 5 , scaling_method = "RobustScaler" , top_n = 10)
        print(f" .... Generando Recomendaciones Terminado ")
        
        #Generar playlist
        df_playlist = df_recomendaciones[["name", "artists"]]
        playlist = "\n".join(df_playlist.apply(lambda row: ' - '.join(row), axis=1))

        print(f'Playlist: {playlist}')

        # remover las recomendaciones en caso que al usuario no le gusten
        canciones_no_gustadas = df_recomendaciones['id'].tolist()
        
        #app.config['g_canciones_no_gustadas'] =  canciones_no_gustadas 
        app.config['g_canciones_no_gustadas'].extend(canciones_no_gustadas)

        print(f'Canciones no Gustadas: {canciones_no_gustadas}')
        return jsonify({'playlist': f'{playlist}'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
