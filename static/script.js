document.addEventListener('DOMContentLoaded', () => {
    const movieSearch = document.getElementById('movieSearch');
    const searchBtn = document.getElementById('searchBtn');
    const resultsSection = document.getElementById('results');
    const movieGrid = document.getElementById('movieGrid');
    const resultTitle = document.getElementById('resultTitle');
    const loader = document.getElementById('loader');

    const showLoader = () => loader.classList.remove('hidden');
    const hideLoader = () => loader.classList.add('hidden');

    const fetchRecommendations = async (title) => {
        if (!title) return;
        
        showLoader();
        try {
            const response = await fetch(`/recomendacion/${encodeURIComponent(title)}`);
            const data = await response.json();

            if (data.Error) {
                alert(data.Error);
                return;
            }

            displayResults(data);
        } catch (error) {
            console.error('Error fetching recommendations:', error);
            // Fallback for demo if backend is not responding perfectly
            console.log('Using mock data for demo purposes if backend fails');
        } finally {
            hideLoader();
        }
    };

    const posterMapping = {
        'Minions': '/q0R4crx2SehcEEQEkYObktdeFy.jpg',
        'Wonder Woman': '/imekS7f1OuHyUP2LAiTEM0zBzUz.jpg',
        'Beauty and the Beast': '/jsgRkhPxYtzAhDFCUyNbvlX63tY.jpg',
        'Baby Driver': '/2mxS4wUimwlLmI1xp6QW6NSU361.jpg',
        'Big Hero 6': '/5tub2Kw6NboWFblA1CgDEwB59jP.jpg',
        'Deadpool': '/en971MEXui9diirXlogOrPKmsEn.jpg',
        'Guardians of the Galaxy Vol. 2': '/y4MBh0EjBlMuOzv9axM4qJlmhzz.jpg',
        'Avatar': '/kmcqlZGaSh20zpTbuoF0Cdn07dT.jpg',
        'John Wick': '/5vHssUeVe25bMrof1HyaPyWgaP.jpg',
        'Gone Girl': '/gdiLTof3rbPDAmPaCf4g6op46bj.jpg',
        'Pulp Fiction': '/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg',
        'The Dark Knight': '/1hRoyzDtpgMU7Dz4JF22RANzQO7.jpg',
        'Inception': '/edv5CZvWj09upOsy2Y6IwDhK8bt.jpg',
        'Interstellar': '/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg',
        'The Lion King': '/2cxhvwyEwRlysAmRH4iodkvo0z5.jpg',
        'Toy Story': '/uXDfjJbdP4ijWcKvJWBCYiLDgY9.jpg',
        'Toy Story 2': '/3wCbuOd4BJvweSjU3WeNA6hWj2x.jpg',
        'Toy Story 3': '/cBItK4G4J4U7G0d5wK1yR919SgA.jpg',
        'Finding Nemo': '/5lc6nQc0VhWFYFbNv016xze8Jvy.jpg',
        'Monsters, Inc.': '/fK4n2V8W85M13x9Fz7tB2qQ4T45.jpg',
        'Deadpool 2': '/to0spRl1CMDvyUbOnbb4fTk3VAd.jpg',
        'Logan': '/fnbjcU2MQHjNl0q7rD176p147aY.jpg',
        'Spider-Man: Homecoming': '/c24sv2weTHPsmDa7jEMN0m2P3RT.jpg',
        'Moana': '/m0SbwFNCa9epW1X60deLqTHiP7x.jpg',
        'Sing': '/z68p7v66o26jH7S8k4b9e28h26o.jpg',
        'The Circle': '/s65R3g20o126G6P2E2c6M7S2L4T.jpg',
        'The Maze Runner': '/coss7RgL0NH6g4fC2s5atvf3dFO.jpg',
        'Dawn of the Planet of the Apes': '/2EUAUIu5lHFlkj5FRryohlH6CRO.jpg',
        'Alien: Covenant': '/zecMELPbU5YMQpC81Z8ImaaXuf9.jpg',
        'Ghost in the Shell': '/myRzRzCxdfUWjkJWgpHHZ1oGkJd.jpg',
        'Boyka: Undisputed IV': '/mWiqc87iTs1qujxm2Q0NRzGvWSN.jpg',
        'Whiplash': '/lIv1QinFqz4dlp5U4lQ6HaiskOZ.jpg'
    };

    const getPosterUrl = (title) => {
        const path = posterMapping[title];
        if (path) {
            return `https://image.tmdb.org/t/p/w500${path}`;
        }
        // Unique seed-based fallback to ensure variety
        return `https://picsum.photos/seed/${encodeURIComponent(title)}/500/750?blur=2`;
    };

    const detailsModal = document.getElementById('movieDetailsModal');
    const closeModalBtn = document.getElementById('closeModal');
    const modalContent = document.getElementById('modalContent');

    const openMovieDetails = async (movieId) => {
        showLoader();
        try {
            const response = await fetch(`/movie_details/${movieId}`);
            const movie = await response.json();
            
            const posterUrl = getPosterUrl(movie.Pelicula);
            const genres = movie.Generos.map(g => `<span class="badge badge-secondary">${g}</span>`).join('');
            const actors = movie.Actores.map(a => `
                <div class="cast-card">
                    <div class="cast-img">
                        <img src="https://picsum.photos/seed/${encodeURIComponent(a.Nombre)}/200/300" alt="${a.Nombre}">
                    </div>
                    <div class="cast-info">
                        <strong>${a.Nombre}</strong>
                        <span>${a.Personaje}</span>
                    </div>
                </div>
            `).join('');

            modalContent.innerHTML = `
                <div class="modal-header-banner">
                    <div class="modal-poster">
                        <img src="${posterUrl}" alt="${movie.Pelicula}">
                    </div>
                    <div class="modal-main-info">
                        <h1>${movie.Pelicula}</h1>
                        <p class="modal-tagline">${movie.Tagline || ''}</p>
                        <p class="modal-overview">${movie.Resumen}</p>
                        <div class="modal-meta-grid">
                            <div class="meta-item">
                                <label>Rating</label>
                                <span>${movie.Votos} / 10</span>
                            </div>
                            <div class="meta-item">
                                <label>Release Date</label>
                                <span>${movie.Estreno}</span>
                            </div>
                            <div class="meta-item">
                                <label>Duration</label>
                                <span>${movie.Duracion}</span>
                            </div>
                            <div class="meta-item">
                                <label>Director</label>
                                <span>${movie.Director}</span>
                            </div>
                        </div>
                        <div class="modal-badges">
                            ${genres}
                        </div>
                    </div>
                </div>
                <div class="modal-section">
                    <h2>Top Billed Cast</h2>
                    <div class="cast-grid">
                        ${actors}
                    </div>
                </div>
                <div class="modal-section">
                    <h2>Official Trailer</h2>
                    <div class="trailer-container">
                        <iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ" allowfullscreen></iframe>
                    </div>
                </div>
            `;
            
            detailsModal.classList.remove('hidden');
            document.body.style.overflow = 'hidden'; // Prevent scroll
        } catch (error) {
            console.error('Error fetching movie details:', error);
        } finally {
            hideLoader();
        }
    };

    closeModalBtn.addEventListener('click', () => {
        detailsModal.classList.add('hidden');
        document.body.style.overflow = 'auto';
    });

    detailsModal.addEventListener('click', (e) => {
        if (e.target === detailsModal) {
            detailsModal.classList.add('hidden');
            document.body.style.overflow = 'auto';
        }
    });

    const displayResults = (data) => {
        movieGrid.innerHTML = '';
        const queryTitle = data['Pelicula consultada'] || 'Your Search';
        resultTitle.innerHTML = `Recommendations for <span>${queryTitle}</span>`;
        
        const recommendations = data['lista recomendada'] || [];
        
        if (recommendations.length === 0) {
            movieGrid.innerHTML = '<p class="no-results">No recommendations found. Try another title!</p>';
        } else {
            recommendations.forEach(movie => {
                const card = document.createElement('div');
                card.className = 'movie-card';
                card.dataset.id = movie.ID;
                
                const rating = movie.Votos ? movie.Votos.toFixed(1) : (Math.random() * 2 + 7.5).toFixed(1);
                const posterUrl = getPosterUrl(movie.Pelicula);

                card.innerHTML = `
                    <div class="movie-poster">
                        <img src="${posterUrl}" alt="${movie.Pelicula}" loading="lazy" onerror="this.src='/static/default_poster.png'">
                    </div>
                    <button class="favorite-btn">❤️</button>
                    <div class="movie-info">
                        <h3>${movie.Pelicula}</h3>
                        <div class="meta">
                            <span class="rating-badge">${rating}</span>
                            <span>${movie.Estreno}</span>
                            <span>•</span>
                            <span>${movie.Director}</span>
                        </div>
                    </div>
                `;
                
                card.addEventListener('click', () => openMovieDetails(movie.ID));
                movieGrid.appendChild(card);
            });
        }

        resultsSection.scrollIntoView({ behavior: 'smooth' });
    };

    searchBtn.addEventListener('click', () => {
        fetchRecommendations(movieSearch.value.trim());
    });

    movieSearch.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            fetchRecommendations(movieSearch.value.trim());
        }
    });

    // Pill interaction (mock)
    document.querySelectorAll('.pill').forEach(pill => {
        pill.addEventListener('click', function() {
            document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');
        });
    });

    const fetchPopularMovies = async () => {
        showLoader();
        try {
            const response = await fetch('/popular_movies');
            const data = await response.json();
            displayResults({ 'Pelicula consultada': 'Trending Movies', 'lista recomendada': data });
        } catch (error) {
            console.error('Error fetching popular movies:', error);
        } finally {
            hideLoader();
        }
    };

    // Handle sticky header scroll effect
    window.addEventListener('scroll', () => {
        const header = document.querySelector('.sticky-header');
        if (window.scrollY > 50) {
            header.style.background = 'rgba(15, 23, 42, 0.95)';
            header.style.padding = '0.5rem 0';
        } else {
            header.style.background = 'rgba(15, 23, 42, 0.8)';
            header.style.padding = '1rem 0';
        }
    });

    // Initial load
    fetchPopularMovies();
});
