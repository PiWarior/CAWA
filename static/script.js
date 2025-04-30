document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM
    const searchBtn = document.getElementById('search-btn');
    const carsContainer = document.getElementById('cars-container');
    const resultCount = document.getElementById('result-count');
    const modal = document.getElementById('description-modal');
    const closeModal = document.getElementById('close-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalLoading = document.getElementById('modal-loading');
    const modalContent = document.getElementById('modal-content');
    const carDetails = document.getElementById('car-details');
    const carDescription = document.getElementById('car-description');
    const addCarBtn = document.getElementById('add-car-btn');
    
    // Fermeture du modal
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    // Fermer le modal si on clique en dehors
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
    
    // Fonction de recherche
    searchBtn.addEventListener('click', searchCars);
    
    // Ajout d'une voiture
    addCarBtn.addEventListener('click', function() {
        const carData = {
            year: document.getElementById('new-annee').value,
            make: document.getElementById('new-marque').value,
            model: document.getElementById('new-modele').value,
            body_styles: document.getElementById('new-style').value
        };

        fetch('/add_car', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(carData)
        })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            searchCars(); // Recharge les voitures
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'ajout: ' + error);
        });
    });
    
    function searchCars() {
        // Récupération des valeurs des filtres
        const marque = document.getElementById('marque').value;
        const annee = document.getElementById('annee').value;
        const modele = document.getElementById('modele').value;
        const bodyStyle = document.getElementById('body_style').value;
        
        // Construction de l'URL avec les paramètres
        const url = `/search_data?marque=${encodeURIComponent(marque)}&annee=${encodeURIComponent(annee)}&modele=${encodeURIComponent(modele)}&body_style=${encodeURIComponent(bodyStyle)}`;
        
        // Affichage d'un message de chargement
        carsContainer.innerHTML = '<div class="loading"><div class="spinner"></div> Chargement des résultats...</div>';
        
        // Requête AJAX pour récupérer les données
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors de la récupération des données de la BDD');
                }
                return response.json();
            })
            .then(data => {
                // Vérification des données reçues
                console.log("Données reçues:", data);
                
                // Mise à jour du compteur de résultats
                resultCount.textContent = `${data.count} voiture(s) trouvée(s)`;
                
                // Effacement du contenu précédent
                carsContainer.innerHTML = '';
                
                // Si aucun résultat
                if (data.count === 0) {
                    carsContainer.innerHTML = '<p>Aucune voiture ne correspond à vos critères de recherche.</p>';
                    return;
                }
                
                // Affichage des résultats
                data.voitures.forEach(car => {
                    const carCard = document.createElement('div');
                    carCard.className = 'car-card';
                    carCard.innerHTML = `
                        <div class="car-title">${car.marque} ${car.modele} (${car.annee})</div>
                        <div class="car-info">
                            <p><span class="label">Marque:</span> <span>${car.marque}</span></p>
                            <p><span class="label">Modèle:</span> <span>${car.modele}</span></p>
                            <p><span class="label">Année:</span> <span>${car.annee}</span></p>
                            <p><span class="label">Style:</span> <span>${car.style}</span></p>
                        </div>
                        <div class="car-actions">
                            <button class="description-btn" data-car-id="${car.id}">Description</button>
                            <button class="delete-btn" data-car-id="${car.id}">Supprimer</button>
                        </div>
                    `;
                    carsContainer.appendChild(carCard);
                    
                    // Ajout de l'événement pour le bouton de description
                    const descBtn = carCard.querySelector('.description-btn');
                    descBtn.addEventListener('click', function() {
                        openDescriptionModal(car);
                    });
                    
                    // Ajout de l'événement pour le bouton de suppression
                    const deleteBtn = carCard.querySelector('.delete-btn');
                    deleteBtn.addEventListener('click', function() {
                        const carId = this.getAttribute('data-car-id');
                        if (confirm("Confirmer la suppression de cette voiture ?")) {
                            fetch(`/delete_car/${carId}`, {
                                method: 'DELETE'
                            })
                            .then(res => res.json())
                            .then(data => {
                                alert(data.message);
                                searchCars(); // Recharger les voitures après la suppression
                            })
                            .catch(error => {
                                console.error('Erreur lors de la suppression:', error);
                                alert('Erreur lors de la suppression: ' + error);
                            });
                        }
                    });
                });
            })
            .catch(error => {
                console.error('Erreur:', error);
                carsContainer.innerHTML = `<p>Une erreur est survenue lors de la recherche: ${error}</p>`;
            });
    }
    
    // Fonction pour ouvrir le modal et charger la description
    function openDescriptionModal(car) {
        // Mise à jour du titre
        modalTitle.textContent = `${car.marque} ${car.modele} (${car.annee})`;
        
        // Affichage du modal et du loader
        modal.style.display = 'block';
        modalLoading.style.display = 'block';
        modalContent.style.display = 'none';
        
        // Requête pour obtenir la description
        fetch(`/get_model_description?car_id=${car.id}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erreur lors de la récupération de la description');
                }
                return response.json();
            })
            .then(data => {
                // Mise à jour des détails
                carDetails.innerHTML = '';
                
                // Affichage des détails de base
                const detailsBase = ['marque', 'modele', 'annee', 'style'];
                detailsBase.forEach(key => {
                    if (data.car_details && data.car_details[key]) {
                        const detailItem = document.createElement('div');
                        detailItem.className = 'detail-item';
                        detailItem.innerHTML = `
                            <div class="detail-label">${key.charAt(0).toUpperCase() + key.slice(1)}</div>
                            <div class="detail-value">${data.car_details[key]}</div>
                        `;
                        carDetails.appendChild(detailItem);
                    }
                });
                
                // Affichage d'autres détails si disponibles
                if (data.car_details && data.car_details.carburant && data.car_details.carburant !== 'Inconnu') {
                    const carburantItem = document.createElement('div');
                    carburantItem.className = 'detail-item';
                    carburantItem.innerHTML = `
                        <div class="detail-label">Carburant</div>
                        <div class="detail-value">${data.car_details.carburant}</div>
                    `;
                    carDetails.appendChild(carburantItem);
                }
                
                if (data.car_details && data.car_details.kilometrage && data.car_details.kilometrage !== 'Inconnu') {
                    const kilometrageItem = document.createElement('div');
                    kilometrageItem.className = 'detail-item';
                    kilometrageItem.innerHTML = `
                        <div class="detail-label">Kilométrage</div>
                        <div class="detail-value">${data.car_details.kilometrage}</div>
                    `;
                    carDetails.appendChild(kilometrageItem);
                }
                
                // Affichage de la description
                carDescription.textContent = data.description || "Aucune description disponible";
                
                // Masquer le loader et afficher le contenu
                modalLoading.style.display = 'none';
                modalContent.style.display = 'block';
            })
            .catch(error => {
                console.error('Erreur:', error);
                carDescription.innerHTML = `<p>Une erreur de connexion est survenue lors de la génération de la description: ${error}</p>`;
                modalLoading.style.display = 'none';
                modalContent.style.display = 'block';
            });
    }
});