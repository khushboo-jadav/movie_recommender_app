import streamlit as st
import pickle
import pandas as pd
import requests
import html

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0f1020 0%, #1f1147 50%, #3a0f3f 100%); }
.hero { text-align: center; padding: 10px 0 25px 0; }
.hero h1 { font-size: 3rem; background: linear-gradient(90deg, #ff4b6e, #ffb347);
           -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { color: #c9c9d6; font-size: 1.1rem; }
.card { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px; overflow: hidden; text-align: center; transition: transform .2s; }
.card:hover { transform: translateY(-6px); border-color: #ff4b6e; }
.card img { width: 100%; height: 330px; object-fit: cover; display: block; }
.poster { height: 330px; display: flex; align-items: center; justify-content: center;
          font-size: 4rem; background: linear-gradient(160deg, #ff4b6e, #7a2cff); }
.title { padding: 12px; font-weight: 600; color: #fff; }
.stButton > button { background: linear-gradient(90deg, #ff4b6e, #ff8a4b); color: white;
                     border: none; border-radius: 10px; padding: 0.6rem 2rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    movies = pd.DataFrame(pickle.load(open('movies_dic.pkl', 'rb'))).reset_index(drop=True)
    neighbors = pickle.load(open('neighbors.pkl', 'rb'))
    return movies, neighbors

movies, neighbors = load_data()

@st.cache_data(show_spinner=False)
def fetch_poster(title):
    try:
        r = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": st.secrets["TMDB_API_KEY"], "query": title},
            timeout=10,
        )
        results = r.json().get("results", [])
        if results and results[0].get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + results[0]["poster_path"]
    except Exception:
        pass
    return None

def recommend(title):
    i = movies[movies['title'] == title].index[0]
    return movies.iloc[neighbors[i][:5]]['title'].tolist()

st.markdown("""
<div class="hero">
  <h1>🎬 Movie Recommender</h1>
  <p>Pick a movie you love, and we'll find your next favourite.</p>
</div>
""", unsafe_allow_html=True)

selected = st.selectbox("Pick a movie you like", movies['title'].values)

if st.button("✨ Recommend"):
    st.subheader("You might also like")
    with st.spinner("Finding movies and posters..."):
        names = recommend(selected)
        posters = [fetch_poster(n) for n in names]
    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            if poster:
                top = '<img src="' + poster + '">'
            else:
                top = '<div class="poster">🎞️</div>'
            card = '<div class="card">' + top + '<div class="title">' + html.escape(name) + '</div></div>'
            st.markdown(card, unsafe_allow_html=True)
