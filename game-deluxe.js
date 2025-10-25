// ====================================================================================
// SALON PAZNOKCI: DELUXE EDITION - Advanced Game Engine
// ====================================================================================

// ==================== CONFIGURATION ====================
const CONFIG = {
    TILE_SIZE: 48,
    PLAYER_SPEED: 4,
    ANIMATION_SPEED: 8,
    PARTICLE_COUNT: 50,
    SHADOW_BLUR: 15,
    LIGHT_RADIUS: 200,
    FPS: 60
};

// ==================== PIXEL ART SPRITES ====================
class SpriteRenderer {
    static drawPlayer(ctx, x, y, direction, frame) {
        ctx.save();
        
        // Shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.beginPath();
        ctx.ellipse(x, y + 28, 12, 6, 0, 0, Math.PI * 2);
        ctx.fill();
        
        // Legs animation
        const legOffset = frame % 2 === 0 ? 2 : -2;
        
        // Left leg
        ctx.fillStyle = '#2d5f3d';
        ctx.fillRect(x - 6, y + 15, 6, 12);
        ctx.fillRect(x - 6, y + 27 + (direction === 'down' ? legOffset : -legOffset), 6, 3);
        
        // Right leg
        ctx.fillRect(x + 2, y + 15, 6, 12);
        ctx.fillRect(x + 2, y + 27 + (direction === 'down' ? -legOffset : legOffset), 6, 3);
        
        // Body
        const bodyColors = {
            main: '#4a90e2',
            dark: '#3a70b2',
            light: '#5aa0f2'
        };
        
        // Main body
        ctx.fillStyle = bodyColors.main;
        ctx.fillRect(x - 10, y - 5, 20, 20);
        
        // Body details
        ctx.fillStyle = bodyColors.dark;
        ctx.fillRect(x - 10, y - 5, 4, 20); // Left side shadow
        ctx.fillStyle = bodyColors.light;
        ctx.fillRect(x + 6, y - 3, 3, 16); // Right highlight
        
        // Arms
        ctx.fillStyle = '#ffdbac';
        if (direction === 'down' || direction === 'up') {
            ctx.fillRect(x - 14, y + 2, 4, 10);
            ctx.fillRect(x + 10, y + 2, 4, 10);
        } else if (direction === 'left') {
            ctx.fillRect(x - 14, y + 2, 4, 10);
            ctx.fillRect(x + 6, y + 2, 4, 10);
        } else {
            ctx.fillRect(x - 10, y + 2, 4, 10);
            ctx.fillRect(x + 10, y + 2, 4, 10);
        }
        
        // Neck
        ctx.fillStyle = '#ffdbac';
        ctx.fillRect(x - 4, y - 8, 8, 4);
        
        // Head
        ctx.fillStyle = '#ffdbac';
        ctx.fillRect(x - 8, y - 20, 16, 16);
        
        // Head outline
        ctx.strokeStyle = '#d4a574';
        ctx.lineWidth = 1;
        ctx.strokeRect(x - 8, y - 20, 16, 16);
        
        // Hair
        ctx.fillStyle = '#3d2817';
        ctx.fillRect(x - 9, y - 22, 18, 8);
        ctx.fillRect(x - 10, y - 20, 20, 4);
        
        // Hair highlights
        ctx.fillStyle = '#5d4837';
        ctx.fillRect(x - 6, y - 21, 2, 6);
        ctx.fillRect(x + 2, y - 21, 2, 6);
        
        // Face features based on direction
        if (direction === 'down') {
            // Eyes
            ctx.fillStyle = '#000';
            ctx.fillRect(x - 5, y - 15, 2, 2);
            ctx.fillRect(x + 3, y - 15, 2, 2);
            
            // Eye whites
            ctx.fillStyle = '#fff';
            ctx.fillRect(x - 5, y - 15, 1, 1);
            ctx.fillRect(x + 3, y - 15, 1, 1);
            
            // Nose
            ctx.fillStyle = '#d4a574';
            ctx.fillRect(x - 1, y - 12, 2, 3);
            
            // Mouth
            ctx.fillStyle = '#8b6f4f';
            ctx.fillRect(x - 2, y - 8, 4, 1);
        } else if (direction === 'up') {
            // Back of head - just hair
            ctx.fillStyle = '#3d2817';
            ctx.fillRect(x - 4, y - 16, 8, 8);
        } else if (direction === 'left') {
            // Side view
            ctx.fillStyle = '#000';
            ctx.fillRect(x - 6, y - 15, 2, 2);
            ctx.fillStyle = '#fff';
            ctx.fillRect(x - 6, y - 15, 1, 1);
            
            ctx.fillStyle = '#d4a574';
            ctx.fillRect(x - 8, y - 12, 2, 2);
        } else {
            // Side view right
            ctx.fillStyle = '#000';
            ctx.fillRect(x + 4, y - 15, 2, 2);
            ctx.fillStyle = '#fff';
            ctx.fillRect(x + 5, y - 15, 1, 1);
            
            ctx.fillStyle = '#d4a574';
            ctx.fillRect(x + 6, y - 12, 2, 2);
        }
        
        ctx.restore();
    }
    
    static drawNPC(ctx, x, y, type, frame) {
        ctx.save();
        
        // Shadow
        ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
        ctx.beginPath();
        ctx.ellipse(x, y + 28, 12, 6, 0, 0, Math.PI * 2);
        ctx.fill();
        
        let bodyColor, hairColor, skinColor;
        
        switch(type) {
            case 'receptionist':
                bodyColor = '#e74c3c';
                hairColor = '#f39c12';
                skinColor = '#ffdbac';
                break;
            case 'stylist':
                bodyColor = '#9b59b6';
                hairColor = '#2c3e50';
                skinColor = '#ffdbac';
                break;
            case 'client':
                bodyColor = '#1abc9c';
                hairColor = '#c0392b';
                skinColor = '#ffdbac';
                break;
            default:
                bodyColor = '#95a5a6';
                hairColor = '#34495e';
                skinColor = '#ffdbac';
        }
        
        // Simplified NPC - similar to player but with different colors
        ctx.fillStyle = bodyColor;
        ctx.fillRect(x - 10, y - 5, 20, 20);
        
        ctx.fillStyle = skinColor;
        ctx.fillRect(x - 8, y - 20, 16, 16);
        
        ctx.fillStyle = hairColor;
        ctx.fillRect(x - 9, y - 22, 18, 8);
        
        // Eyes
        ctx.fillStyle = '#000';
        ctx.fillRect(x - 5, y - 15, 2, 2);
        ctx.fillRect(x + 3, y - 15, 2, 2);
        
        ctx.restore();
    }
    
    static drawObject(ctx, obj) {
        ctx.save();
        
        // Shadow
        if (obj.castShadow !== false) {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
            ctx.fillRect(obj.x + 3, obj.y + obj.height - 3, obj.width, 5);
        }
        
        // Main object
        if (obj.gradient) {
            const gradient = ctx.createLinearGradient(
                obj.x, obj.y,
                obj.x, obj.y + obj.height
            );
            gradient.addColorStop(0, obj.gradient.start);
            gradient.addColorStop(1, obj.gradient.end);
            ctx.fillStyle = gradient;
        } else {
            ctx.fillStyle = obj.color;
        }
        
        if (obj.shape === 'circle') {
            ctx.beginPath();
            ctx.arc(obj.x + obj.width/2, obj.y + obj.height/2, obj.width/2, 0, Math.PI * 2);
            ctx.fill();
        } else {
            ctx.fillRect(obj.x, obj.y, obj.width, obj.height);
        }
        
        // Outline
        ctx.strokeStyle = obj.outlineColor || '#000';
        ctx.lineWidth = 2;
        if (obj.shape === 'circle') {
            ctx.beginPath();
            ctx.arc(obj.x + obj.width/2, obj.y + obj.height/2, obj.width/2, 0, Math.PI * 2);
            ctx.stroke();
        } else {
            ctx.strokeRect(obj.x, obj.y, obj.width, obj.height);
        }
        
        // Object-specific details
        if (obj.type === 'desk') {
            // Desk legs
            ctx.fillStyle = '#3a2f25';
            ctx.fillRect(obj.x + 10, obj.y + obj.height - 10, 8, 10);
            ctx.fillRect(obj.x + obj.width - 18, obj.y + obj.height - 10, 8, 10);
            
            // Desk top highlight
            ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
            ctx.fillRect(obj.x + 5, obj.y + 5, obj.width - 10, 10);
        } else if (obj.type === 'door') {
            // Door handle
            ctx.fillStyle = '#ffd700';
            ctx.fillRect(obj.x + obj.width - 15, obj.y + obj.height/2 - 4, 8, 8);
            
            // Door frame
            ctx.strokeStyle = '#5d4e37';
            ctx.lineWidth = 4;
            ctx.strokeRect(obj.x, obj.y, obj.width, obj.height);
            
            // Door panels
            ctx.strokeStyle = '#4a3828';
            ctx.lineWidth = 2;
            ctx.strokeRect(obj.x + 10, obj.y + 10, obj.width - 20, obj.height/2 - 15);
            ctx.strokeRect(obj.x + 10, obj.y + obj.height/2 + 5, obj.width - 20, obj.height/2 - 15);
        } else if (obj.type === 'chair') {
            // Chair back
            ctx.fillStyle = obj.color;
            ctx.fillRect(obj.x + 10, obj.y, obj.width - 20, 15);
            
            // Chair legs
            ctx.fillStyle = '#3a2f25';
            ctx.fillRect(obj.x + 8, obj.y + obj.height - 8, 6, 8);
            ctx.fillRect(obj.x + obj.width - 14, obj.y + obj.height - 8, 6, 8);
        } else if (obj.type === 'plant') {
            // Pot
            ctx.fillStyle = '#8b4513';
            ctx.fillRect(obj.x + 8, obj.y + obj.height - 20, obj.width - 16, 20);
            
            // Leaves
            ctx.fillStyle = obj.dead ? '#6b5d4f' : '#2d5016';
            for (let i = 0; i < 5; i++) {
                const leafX = obj.x + obj.width/2 + (Math.cos(i * Math.PI * 0.4) * 15);
                const leafY = obj.y + 10 + (Math.sin(i * Math.PI * 0.4) * 15);
                ctx.beginPath();
                ctx.arc(leafX, leafY, 8, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        
        // Interactive indicator
        if (obj.interactive && obj.showIndicator) {
            const time = Date.now() / 1000;
            const bounce = Math.sin(time * 3) * 5;
            
            ctx.fillStyle = '#e74c3c';
            ctx.beginPath();
            ctx.arc(obj.x + obj.width/2, obj.y - 20 + bounce, 10, 0, Math.PI * 2);
            ctx.fill();
            
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 14px Courier New';
            ctx.textAlign = 'center';
            ctx.fillText('E', obj.x + obj.width/2, obj.y - 16 + bounce);
        }
        
        ctx.restore();
    }
}

// ==================== PARTICLE SYSTEM ====================
class Particle {
    constructor(x, y, color, velocity, lifetime) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.vx = velocity.x;
        this.vy = velocity.y;
        this.lifetime = lifetime;
        this.age = 0;
        this.size = Math.random() * 3 + 1;
    }
    
    update(dt) {
        this.x += this.vx * dt;
        this.y += this.vy * dt;
        this.vy += 0.3 * dt; // Gravity
        this.age += dt;
        return this.age < this.lifetime;
    }
    
    draw(ctx) {
        const alpha = 1 - (this.age / this.lifetime);
        ctx.fillStyle = this.color.replace(')', `, ${alpha})`).replace('rgb', 'rgba');
        ctx.fillRect(this.x, this.y, this.size, this.size);
    }
}

class ParticleSystem {
    constructor() {
        this.particles = [];
    }
    
    emit(x, y, count, color = 'rgb(255, 200, 100)') {
        for (let i = 0; i < count; i++) {
            const angle = (Math.PI * 2 * i) / count;
            const speed = Math.random() * 50 + 20;
            this.particles.push(new Particle(
                x, y, color,
                { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed },
                Math.random() * 0.5 + 0.5
            ));
        }
    }
    
    update(dt) {
        this.particles = this.particles.filter(p => p.update(dt));
    }
    
    draw(ctx) {
        this.particles.forEach(p => p.draw(ctx));
    }
}


// ==================== GAME STATE ====================
class GameState {
    constructor() {
        this.currentRoom = 'entrance';
        this.player = {
            x: 480,
            y: 400,
            direction: 'down',
            speed: CONFIG.PLAYER_SPEED,
            animFrame: 0,
            animTimer: 0
        };
        this.inventory = [];
        this.clues = [];
        this.objectives = [];
        this.flags = {};
        this.dialogActive = false;
        this.currentDialog = null;
        this.visitedRooms = new Set();
        this.achievements = [];
        this.particles = new ParticleSystem();
        this.npcs = [];
        this.timeElapsed = 0;
        this.interactionsCount = 0;
    }
    
    addItem(id, name, description, icon = '📦') {
        if (!this.inventory.find(item => item.id === id)) {
            this.inventory.push({ id, name, description, icon, type: 'item' });
            this.updateUI();
            this.checkAchievements();
        }
    }
    
    addClue(id, name, description, icon = '📋') {
        if (!this.clues.find(clue => clue.id === id)) {
            this.clues.push({ id, name, description, icon, type: 'clue' });
            this.updateUI();
            this.addJournalEntry(`Nowa wskazówka: ${name}`, description);
            this.checkAchievements();
        }
    }
    
    addObjective(text, completed = false) {
        if (!this.objectives.find(obj => obj.text === text)) {
            this.objectives.push({ text, completed });
            this.updateUI();
        }
    }
    
    completeObjective(text) {
        const obj = this.objectives.find(o => o.text === text);
        if (obj && !obj.completed) {
            obj.completed = true;
            this.updateUI();
            this.particles.emit(480, 100, 20, 'rgb(46, 204, 113)');
            this.checkAchievements();
        }
    }
    
    addAchievement(id, name, description) {
        if (!this.achievements.find(a => a.id === id)) {
            this.achievements.push({ id, name, description });
            this.showAchievement(name, description);
            this.updateUI();
        }
    }
    
    showAchievement(name, description) {
        const popup = document.createElement('div');
        popup.className = 'achievement-popup';
        popup.innerHTML = `<span class="achievement-icon">🏆</span><strong>${name}</strong><br><small>${description}</small>`;
        document.body.appendChild(popup);
        setTimeout(() => document.body.removeChild(popup), 4000);
    }
    
    addJournalEntry(title, content) {
        const journalContent = document.getElementById('journal-content');
        const entry = document.createElement('div');
        entry.className = 'objective-item';
        entry.innerHTML = `<strong>${title}</strong><br><small>${content}</small>`;
        journalContent.insertBefore(entry, journalContent.firstChild);
    }
    
    checkAchievements() {
        if (this.clues.length >= 5 && !this.achievements.find(a => a.id === 'detective')) {
            this.addAchievement('detective', 'Detektyw', 'Zebrałeś 5 wskazówek');
        }
        if (this.inventory.length >= 10 && !this.achievements.find(a => a.id === 'collector')) {
            this.addAchievement('collector', 'Kolekcjoner', 'Zebrałeś 10 przedmiotów');
        }
        if (this.visitedRooms.size >= 10 && !this.achievements.find(a => a.id === 'explorer')) {
            this.addAchievement('explorer', 'Odkrywca', 'Odwiedziłeś 10 pokoi');
        }
    }
    
    updateUI() {
        // Update objectives
        const objectivesList = document.getElementById('objectives-list');
        objectivesList.innerHTML = '';
        this.objectives.forEach(obj => {
            const div = document.createElement('div');
            div.className = 'objective-item' + (obj.completed ? ' completed' : '');
            div.textContent = (obj.completed ? '✓ ' : '○ ') + obj.text;
            objectivesList.appendChild(div);
        });
        
        // Update inventory
        const inventoryList = document.getElementById('inventory-list');
        inventoryList.innerHTML = '';
        
        [...this.inventory, ...this.clues].forEach(item => {
            const div = document.createElement('div');
            div.className = item.type === 'clue' ? 'inventory-item clue-item' : 'inventory-item';
            div.innerHTML = `
                <span class="icon">${item.icon}</span>
                <div class="details">
                    <div class="name">${item.name}</div>
                    <div class="desc">${item.description}</div>
                </div>
            `;
            inventoryList.appendChild(div);
        });
        
        // Update stats
        document.getElementById('stat-clues').textContent = this.clues.length;
        document.getElementById('stat-items').textContent = this.inventory.length;
        document.getElementById('stat-rooms').textContent = `${this.visitedRooms.size}/15`;
        document.getElementById('stat-achievements').textContent = `${this.achievements.length}/20`;
    }
}

// ==================== ROOMS DEFINITION ====================
const ROOMS = {
    entrance: {
        name: 'Wejście do Salonu',
        bgColor: '#2d2d44',
        floorColor: '#3d3d5d',
        lighting: 0.8,
        ambientParticles: true,
        music: 'ambient',
        objects: [
            {
                id: 'reception',
                type: 'desk',
                x: 380, y: 150,
                width: 200, height: 100,
                color: '#6b4e3d',
                gradient: { start: '#7b5e4d', end: '#5b3e2d' },
                interactive: true,
                name: 'Recepcja',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addClue('terminarz', 'Terminarz', 'Ostatni wpis: "Natalia - 18:00 - paznokcie żelowe"', '📅');
                        game.showNotification('Znaleziono terminarz!');
                        game.addObjective('Sprawdź pokój manicure');
                        game.particles.emit(this.x + this.width/2, this.y, 15, 'rgb(255, 215, 0)');
                        return 'Na recepcji leży otwarty terminarz. Ostatni wpis dotyczy Natalii...';
                    }
                    return 'Recepcja jest pusta i zakurzona.';
                }
            },
            {
                id: 'sofa',
                type: 'furniture',
                x: 100, y: 400,
                width: 180, height: 90,
                color: '#6b4c7a',
                gradient: { start: '#7b5c8a', end: '#5b3c6a' },
                interactive: true,
                name: 'Sofa dla klientów',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        return 'Stara, wystrzępiona sofa. Pod poduszkami znajdujesz drobne monety.';
                    }
                    return 'Niezbyt wygodna sofa.';
                }
            },
            {
                id: 'plant1',
                type: 'plant',
                x: 750, y: 500,
                width: 50, height: 80,
                color: '#2d5016',
                interactive: true,
                dead: true,
                name: 'Uschnięta roślina',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addClue('wizytowka', 'Wizytówka psychologa', 'Dr Kowalski - Psycholog - 555-0123', '💼');
                        return 'W ziemi pod rośliną znajdujesz wizytówkę psychologa!';
                    }
                    return 'Dawno uschnięta roślina.';
                }
            },
            {
                id: 'door_manicure',
                type: 'door',
                x: 850, y: 300,
                width: 80, height: 140,
                color: '#8b6f47',
                interactive: true,
                destination: 'manicure_room',
                name: 'Drzwi do pokoju manicure'
            },
            {
                id: 'door_exit',
                type: 'door',
                x: 30, y: 300,
                width: 80, height: 140,
                color: '#654321',
                interactive: true,
                locked: true,
                name: 'Drzwi wejściowe',
                onInteract: function(game) {
                    return 'Drzwi są zamknięte. Nie możesz stąd wyjść bez rozwiązania zagadki.';
                }
            }
        ]
    },
    
    manicure_room: {
        name: 'Pokój Manicure',
        bgColor: '#3d2d44',
        floorColor: '#4d3d5d',
        lighting: 0.85,
        objects: [
            {
                id: 'station1',
                type: 'desk',
                x: 150, y: 200,
                width: 140, height: 100,
                color: '#5d4037',
                interactive: true,
                name: 'Stanowisko 1',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addClue('pilnik', 'Pilnik z inicjałami N.K.', 'Pilnik do paznokci z wygrawerowanymi inicjałami', '📝');
                        game.addItem('pilnik_item', 'Pilnik', 'Może się przydać', '🔧');
                        game.particles.emit(this.x + this.width/2, this.y, 20);
                        return 'Stanowisko wygląda jakby ktoś nagle przerwał pracę. Znajdujesz pilnik z inicjałami "N.K."!';
                    }
                    return 'Stanowisko do manicure.';
                }
            },
            {
                id: 'station2',
                type: 'desk',
                x: 380, y: 200,
                width: 140, height: 100,
                color: '#5d4037',
                interactive: true,
                name: 'Stanowisko 2',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        return 'Buteleczki z lakierem przewrócone. Ktoś tu szybko opuścił miejsce.';
                    }
                    return 'Stanowisko z lampą UV.';
                }
            },
            {
                id: 'station3',
                type: 'desk',
                x: 610, y: 200,
                width: 140, height: 100,
                color: '#5d4037',
                interactive: true,
                name: 'Stanowisko 3',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addClue('photo', 'Zdjęcie zespołu', 'Natalia z koleżankami. Wszyscy się uśmiechają. "Najlepszy zespół 2023!"', '📸');
                        return 'Najczystsze stanowisko. Znajdujesz zdjęcie Natalii z zespołem!';
                    }
                    return 'Niezużywane stanowisko.';
                }
            },
            {
                id: 'cabinet',
                type: 'furniture',
                x: 800, y: 150,
                width: 120, height: 180,
                color: '#546e7a',
                interactive: true,
                name: 'Szafka z przyborami',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addClue('note_basement', 'Notatka', 'Lista zakupów z dopiskiem: "Natalia - spotkanie w piwnicy 18:30"', '📄');
                        game.addObjective('Znajdź wejście do piwnicy');
                        game.showNotification('Ważna wskazówka o piwnicy!');
                        return 'W szafce znajdujesz notatkę o spotkaniu w piwnicy!';
                    }
                    return 'Szafka z narzędziami i lakierami.';
                }
            },
            {
                id: 'door_back',
                type: 'door',
                x: 850, y: 500,
                width: 80, height: 140,
                color: '#8b6f47',
                interactive: true,
                destination: 'backroom',
                name: 'Drzwi do zaplecza'
            },
            {
                id: 'door_entrance',
                type: 'door',
                x: 30, y: 500,
                width: 80, height: 140,
                color: '#8b6f47',
                interactive: true,
                destination: 'entrance',
                name: 'Powrót do wejścia'
            }
        ]
    },
    
    backroom: {
        name: 'Zaplecze',
        bgColor: '#2d2d2d',
        floorColor: '#3d3d3d',
        lighting: 0.7,
        objects: [
            {
                id: 'locker_natalia',
                type: 'furniture',
                x: 400, y: 150,
                width: 100, height: 160,
                color: '#546e7a',
                interactive: true,
                locked: true,
                name: 'Szafka Natalii',
                examined: false,
                requiredItem: 'small_key',
                onInteract: function(game) {
                    if (this.locked) {
                        if (game.inventory.find(i => i.id === 'small_key')) {
                            this.locked = false;
                            game.showNotification('Szafka otwarta!');
                            game.addClue('natalia_phone', 'Telefon Natalii', 'SMS: "Spotkajmy się w piwnicy. Mam dowody." - od nieznanego', '📱');
                            game.addClue('natalia_note', 'Notatka Natalii', 'Marta nie popełniła samobójstwa. Mam dowody w sejfie.', '📝');
                            game.particles.emit(this.x + this.width/2, this.y, 30, 'rgb(46, 204, 113)');
                            game.flags.opened_natalia_locker = true;
                            return 'Szafka otwarta! Telefon i notatka Natalii!';
                        }
                        return 'Zamknięte na kłódkę. Potrzebujesz małego klucza.';
                    }
                    return 'Szafka Natalii - już sprawdzona.';
                }
            },
            {
                id: 'cleaning_closet',
                type: 'furniture',
                x: 700, y: 450,
                width: 100, height: 140,
                color: '#757575',
                interactive: true,
                name: 'Środki czystości',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addItem('small_key', 'Mały klucz', 'Klucz znaleziony za butelkami', '🔑');
                        game.showNotification('Znaleziono klucz!');
                        game.particles.emit(this.x + this.width/2, this.y, 25, 'rgb(241, 196, 15)');
                        return 'Za butelkami z detergentami znajdujesz mały klucz!';
                    }
                    return 'Szafka ze środkami czystości.';
                }
            },
            {
                id: 'door_office',
                type: 'door',
                x: 150, y: 500,
                width: 80, height: 140,
                color: '#8b6f47',
                interactive: true,
                destination: 'office',
                name: 'Drzwi do biura'
            },
            {
                id: 'door_basement',
                type: 'door',
                x: 850, y: 500,
                width: 80, height: 140,
                color: '#4a4a4a',
                interactive: true,
                destination: 'basement',
                locked: true,
                requiredItem: 'basement_key',
                name: 'Drzwi do piwnicy',
                onInteract: function(game) {
                    if (this.locked) {
                        if (game.inventory.find(i => i.id === 'basement_key')) {
                            this.locked = false;
                            game.showNotification('Piwnica otwarta!');
                            game.addObjective('Zbadaj piwnicę');
                            return 'Drzwi się otworzyły... prowadzą w ciemność.';
                        }
                        return 'Drzwi zamknięte. Potrzebujesz klucza do piwnicy.';
                    }
                    return 'Otwarte drzwi do piwnicy.';
                }
            },
            {
                id: 'door_manicure',
                type: 'door',
                x: 30, y: 300,
                width: 80, height: 140,
                color: '#8b6f47',
                interactive: true,
                destination: 'manicure_room',
                name: 'Powrót do pokoju manicure'
            }
        ]
    },
    
    office: {
        name: 'Biuro Właścicielki',
        bgColor: '#3d2d3d',
        floorColor: '#4d3d4d',
        lighting: 0.75,
        objects: [
            {
                id: 'desk_office',
                type: 'desk',
                x: 350, y: 200,
                width: 260, height: 120,
                color: '#3e2723',
                interactive: true,
                name: 'Biurko właścicielki',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addClue('financial_docs', 'Dokumenty finansowe', 'Salon ma długi 200,000 zł!', '💰');
                        game.addClue('insurance', 'Polisa ubezpieczeniowa', 'Beneficjent śmierci pracownika: 500,000 zł', '📋');
                        game.showNotification('Szokujące odkrycie!');
                        game.particles.emit(this.x + this.width/2, this.y, 40, 'rgb(231, 76, 60)');
                        return 'Dokumenty pokazują desperacką sytuację finansową i... polis  ubezpieczeniową!';
                    }
                    return 'Biurko właścicielki.';
                }
            },
            {
                id: 'safe',
                type: 'furniture',
                x: 150, y: 400,
                width: 100, height: 120,
                color: '#37474f',
                interactive: true,
                locked: true,
                name: 'Sejf',
                code: '2407',
                onInteract: function(game) {
                    if (this.locked) {
                        if (game.flags.knows_safe_code) {
                            // Mini-game: code breaking
                            game.startMiniGame('safe', this);
                            return null;
                        }
                        return 'Sejf wymaga 4-cyfrowego kodu. Musi być wskazówka...';
                    }
                    return 'Sejf już otwarty.';
                }
            },
            {
                id: 'calendar',
                type: 'decoration',
                x: 250, y: 100,
                width: 80, height: 100,
                color: '#fff',
                outlineColor: '#000',
                interactive: true,
                name: 'Kalendarz',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.flags.knows_safe_code = true;
                        game.showNotification('24.07 - może to kod?');
                        return 'Data 24.07 jest zakreślona czerwonym markerem!';
                    }
                    return 'Kalendarz z zakreśloną datą.';
                }
            },
            {
                id: 'door_backroom',
                type: 'door',
                x: 850, y: 500,
                width: 80, height: 140,
                color: '#8b6f47',
                interactive: true,
                destination: 'backroom',
                name: 'Powrót do zaplecza'
            }
        ]
    },
    
    basement: {
        name: 'Piwnica',
        bgColor: '#0a0a0a',
        floorColor: '#1a1a1a',
        lighting: 0.4,
        ambientParticles: true,
        objects: [
            {
                id: 'shelf',
                type: 'furniture',
                x: 700, y: 350,
                width: 100, height: 180,
                color: '#5d4037',
                interactive: true,
                name: 'Regał',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.flags.found_hidden_door = true;
                        game.showNotification('Regał się przesunął!');
                        game.particles.emit(this.x, this.y + this.height/2, 50, 'rgb(189, 195, 199)');
                        const hiddenDoor = ROOMS.basement.objects.find(o => o.id === 'hidden_door');
                        if (hiddenDoor) hiddenDoor.locked = false;
                        return 'Gdy dotykasz regału, przesuwa się odkrywając ukryte drzwi!';
                    }
                    return 'Przesunięty regał.';
                }
            },
            {
                id: 'hidden_door',
                type: 'door',
                x: 820, y: 360,
                width: 70, height: 120,
                color: '#2d2d2d',
                interactive: true,
                locked: true,
                destination: 'hidden_room',
                name: 'Ukryte drzwi',
                onInteract: function(game) {
                    if (this.locked) {
                        return 'Ukryte drzwi. Są zamknięte.';
                    }
                    return 'Ukryte drzwi - możesz przejść.';
                }
            },
            {
                id: 'stairs',
                type: 'furniture',
                x: 80, y: 580,
                width: 120, height: 80,
                color: '#6d6d6d',
                interactive: true,
                destination: 'backroom',
                name: 'Schody w górę'
            }
        ]
    },
    
    hidden_room: {
        name: 'Ukryte Pomieszczenie',
        bgColor: '#050505',
        floorColor: '#0d0d0d',
        lighting: 0.3,
        objects: [
            {
                id: 'natalia_rescued',
                type: 'npc',
                npcType: 'natalia',
                x: 480, y: 360,
                width: 40, height: 60,
                color: '#ff6b9d',
                interactive: true,
                name: '!!! NATALIA !!!',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.flags.found_natalia = true;
                        game.showNotification('🎉 NATALIA ZNALEZIONA! 🎉');
                        game.addObjective('Uratuj Natalię!');
                        game.completeObjective('Znajdź Natalię');
                        game.particles.emit(this.x, this.y, 100, 'rgb(255, 215, 0)');
                        game.startDialog({
                            speaker: 'Natalia',
                            text: 'Znalazłeś mnie! Właścicielka... ona zamknęła mnie tutaj! Chciała uciszyć, tak jak Martę! Mam dowody w biurze!',
                            choices: [
                                { text: 'Jesteś bezpieczna!', action: () => game.checkGameEnd() }
                            ]
                        });
                        return null;
                    }
                    return 'Natalia jest bezpieczna teraz.';
                }
            },
            {
                id: 'evidence_board',
                type: 'furniture',
                x: 250, y: 150,
                width: 460, height: 250,
                color: '#4a4a4a',
                interactive: true,
                name: 'Tablica z dowodami',
                examined: false,
                onInteract: function(game) {
                    if (!this.examined) {
                        this.examined = true;
                        game.addClue('full_story', 'Pełna historia', 'Właścicielka zabiła Martę dla ubezpieczenia. Natalia prowadziła śledztwo.', '📚');
                        game.flags.knows_full_story = true;
                        return 'Cała historia spisana - od początku do końca. Morderstwo inscenizowane jako samobójstwo!';
                    }
                    return 'Tablica dowodów Natalii.';
                }
            },
            {
                id: 'door_basement',
                type: 'door',
                x: 50, y: 580,
                width: 80, height: 100,
                color: '#2d2d2d',
                interactive: true,
                destination: 'basement',
                name: 'Powrót do piwnicy'
            }
        ]
    }
};

