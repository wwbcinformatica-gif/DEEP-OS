// ========================================
// 🏓 PONG - GAME ENGINE
// Fliperama Retrô - HTML5 Canvas
// ========================================

const canvas = document.getElementById('pong-canvas');
const ctx = canvas.getContext('2d');

// --- Dimensões ---
const GAME_WIDTH = 800;
const GAME_HEIGHT = 500;
canvas.width = GAME_WIDTH;
canvas.height = GAME_HEIGHT;

// --- Elementos DOM ---
const scoreP1El = document.getElementById('score-p1');
const scoreP2El = document.getElementById('score-p2');
const messageEl = document.getElementById('game-message');
const overlayEl = document.getElementById('message-overlay');

// ========================================
// ESTADO DO JOGO
// ========================================
const WIN_SCORE = 7;
let gameRunning = false;
let gameOver = false;
let scores = { p1: 0, p2: 0 };

// ========================================
// RAQUETES
// ========================================
const PADDLE_WIDTH = 15;
const PADDLE_HEIGHT = 90;
const PADDLE_SPEED = 7;
const PADDLE_MARGIN = 20;

const paddle1 = {
    x: PADDLE_MARGIN,
    y: GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2,
    w: PADDLE_WIDTH,
    h: PADDLE_HEIGHT,
    dy: 0,
    color: '#00ff88'
};

const paddle2 = {
    x: GAME_WIDTH - PADDLE_MARGIN - PADDLE_WIDTH,
    y: GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2,
    w: PADDLE_WIDTH,
    h: PADDLE_HEIGHT,
    dy: 0,
    color: '#ff0055'
};

// ========================================
// BOLA
// ========================================
const BALL_SIZE = 12;
const BALL_SPEED_INITIAL = 5;
const BALL_SPEED_INCREMENT = 0.3;
let ballSpeed = BALL_SPEED_INITIAL;

const ball = {
    x: GAME_WIDTH / 2,
    y: GAME_HEIGHT / 2,
    size: BALL_SIZE,
    dx: 0,
    dy: 0,
    color: '#ffffff'
};

// ========================================
// PARTÍCULAS (efeito de colisão)
// ========================================
let particles = [];

function createParticles(x, y, color, count = 10) {
    for (let i = 0; i < count; i++) {
        particles.push({
            x: x,
            y: y,
            dx: (Math.random() - 0.5) * 8,
            dy: (Math.random() - 0.5) * 8,
            life: 1.0,
            decay: Math.random() * 0.03 + 0.02,
            size: Math.random() * 4 + 2,
            color: color
        });
    }
}

function updateParticles() {
    for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.dx;
        p.y += p.dy;
        p.life -= p.decay;
        if (p.life <= 0) {
            particles.splice(i, 1);
        }
    }
}

function drawParticles() {
    particles.forEach(p => {
        ctx.globalAlpha = p.life;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();
    });
    ctx.globalAlpha = 1.0;
}

// ========================================
// INICIALIZAÇÃO
// ========================================
function resetBall(direction = 1) {
    ball.x = GAME_WIDTH / 2;
    ball.y = GAME_HEIGHT / 2;
    const angle = (Math.random() - 0.5) * Math.PI / 3; // ±30°
    ball.dx = direction * ballSpeed * Math.cos(angle);
    ball.dy = ballSpeed * Math.sin(angle);
}

function resetGame() {
    scores.p1 = 0;
    scores.p2 = 0;
    ballSpeed = BALL_SPEED_INITIAL;
    updateScoreDisplay();
    paddle1.y = GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2;
    paddle2.y = GAME_HEIGHT / 2 - PADDLE_HEIGHT / 2;
    paddle1.dy = 0;
    paddle2.dy = 0;
    gameOver = false;
    resetBall(Math.random() > 0.5 ? 1 : -1);
}

function startGame() {
    resetGame();
    gameRunning = true;
    overlayEl.style.display = 'none';
}

// ========================================
// INPUT - TECLADO
// ========================================
const keys = {};

document.addEventListener('keydown', (e) => {
    keys[e.key.toLowerCase()] = true;
    keys[e.code] = true;

    // Espaço = iniciar
    if (e.code === 'Space' && !gameRunning && !gameOver) {
        e.preventDefault();
        startGame();
    }

    // R = reiniciar
    if (e.key.toLowerCase() === 'r') {
        startGame();
    }

    // Prevenir scroll com setas
    if (['ArrowUp', 'ArrowDown', 'Space'].includes(e.code)) {
        e.preventDefault();
    }
});

document.addEventListener('keyup', (e) => {
    keys[e.key.toLowerCase()] = false;
    keys[e.code] = false;
});

// ========================================
// INPUT - MOBILE (Touch Buttons)
// ========================================
function setupMobileButton(id, keyCode) {
    const btn = document.getElementById(id);
    if (!btn) return;

    btn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        keys[keyCode] = true;
        btn.classList.add('active');

        // Iniciar jogo no toque
        if (!gameRunning && !gameOver) {
            startGame();
        }
    }, { passive: false });

    btn.addEventListener('touchend', (e) => {
        e.preventDefault();
        keys[keyCode] = false;
        btn.classList.remove('active');
    }, { passive: false });

    btn.addEventListener('touchcancel', (e) => {
        keys[keyCode] = false;
        btn.classList.remove('active');
    });
}

setupMobileButton('p1-up', 'w');
setupMobileButton('p1-down', 's');
setupMobileButton('p2-up', 'ArrowUp');
setupMobileButton('p2-down', 'ArrowDown');

// ========================================
// LÓGICA DO JOGO
// ========================================
function processInput() {
    // Jogador 1 (W/S)
    paddle1.dy = 0;
    if (keys['w']) paddle1.dy = -PADDLE_SPEED;
    if (keys['s']) paddle1.dy = PADDLE_SPEED;

    // Jogador 2 (Setas)
    paddle2.dy = 0;
    if (keys['ArrowUp']) paddle2.dy = -PADDLE_SPEED;
    if (keys['ArrowDown']) paddle2.dy = PADDLE_SPEED;
}

function updatePaddles() {
    paddle1.y += paddle1.dy;
    paddle2.y += paddle2.dy;

    // Limitar dentro do canvas
    paddle1.y = Math.max(0, Math.min(GAME_HEIGHT - PADDLE_HEIGHT, paddle1.y));
    paddle2.y = Math.max(0, Math.min(GAME_HEIGHT - PADDLE_HEIGHT, paddle2.y));
}

function updateBall() {
    ball.x += ball.dx;
    ball.y += ball.dy;

    // Colisão com teto e chão
    if (ball.y - ball.size / 2 <= 0) {
        ball.y = ball.size / 2;
        ball.dy = Math.abs(ball.dy);
        createParticles(ball.x, ball.y, '#ffff00', 5);
    }
    if (ball.y + ball.size / 2 >= GAME_HEIGHT) {
        ball.y = GAME_HEIGHT - ball.size / 2;
        ball.dy = -Math.abs(ball.dy);
        createParticles(ball.x, ball.y, '#ffff00', 5);
    }

    // Colisão com Raquete 1
    if (
        ball.dx < 0 &&
        ball.x - ball.size / 2 <= paddle1.x + paddle1.w &&
        ball.x + ball.size / 2 >= paddle1.x &&
        ball.y + ball.size / 2 >= paddle1.y &&
        ball.y - ball.size / 2 <= paddle1.y + paddle1.h
    ) {
        // Ângulo baseado onde a bola acertou na raquete
        const hitPos = (ball.y - paddle1.y) / paddle1.h; // 0 a 1
        const angle = (hitPos - 0.5) * (Math.PI / 3); // ±60°
        ballSpeed += BALL_SPEED_INCREMENT;
        ball.dx = ballSpeed * Math.cos(angle);
        ball.dy = ballSpeed * Math.sin(angle);
        ball.x = paddle1.x + paddle1.w + ball.size / 2;
        createParticles(ball.x, ball.y, paddle1.color, 12);
    }

    // Colisão com Raquete 2
    if (
        ball.dx > 0 &&
        ball.x + ball.size / 2 >= paddle2.x &&
        ball.x - ball.size / 2 <= paddle2.x + paddle2.w &&
        ball.y + ball.size / 2 >= paddle2.y &&
        ball.y - ball.size / 2 <= paddle2.y + paddle2.h
    ) {
        const hitPos = (ball.y - paddle2.y) / paddle2.h;
        const angle = (hitPos - 0.5) * (Math.PI / 3);
        ballSpeed += BALL_SPEED_INCREMENT;
        ball.dx = -ballSpeed * Math.cos(angle);
        ball.dy = ballSpeed * Math.sin(angle);
        ball.x = paddle2.x - ball.size / 2;
        createParticles(ball.x, ball.y, paddle2.color, 12);
    }

    // Ponto marcado
    if (ball.x < -ball.size) {
        scores.p2++;
        createParticles(0, ball.y, '#ff0055', 20);
        checkWin();
        if (!gameOver) resetBall(-1);
    }

    if (ball.x > GAME_WIDTH + ball.size) {
        scores.p1++;
        createParticles(GAME_WIDTH, ball.y, '#00ff88', 20);
        checkWin();
        if (!gameOver) resetBall(1);
    }
}

function checkWin() {
    updateScoreDisplay();
    if (scores.p1 >= WIN_SCORE || scores.p2 >= WIN_SCORE) {
        gameOver = true;
        gameRunning = false;
        const winner = scores.p1 >= WIN_SCORE ? '🟢 JOGADOR 1' : '🔴 JOGADOR 2';
        showMessage(`${winner} VENCEU! 🏆\nPressione R para jogar novamente`);
    }
}

function updateScoreDisplay() {
    scoreP1El.textContent = scores.p1;
    scoreP2El.textContent = scores.p2;
}

function showMessage(text) {
    overlayEl.style.display = 'flex';
    messageEl.textContent = text;
}

// ========================================
// RENDERIZAÇÃO
// ========================================
function draw() {
    // Fundo
    ctx.fillStyle = '#111111';
    ctx.fillRect(0, 0, GAME_WIDTH, GAME_HEIGHT);

    // Linha central (traços)
    ctx.setLineDash([10, 10]);
    ctx.strokeStyle = '#333333';
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(GAME_WIDTH / 2, 0);
    ctx.lineTo(GAME_WIDTH / 2, GAME_HEIGHT);
    ctx.stroke();
    ctx.setLineDash([]);

    // Raquete 1
    ctx.shadowColor = paddle1.color;
    ctx.shadowBlur = 15;
    ctx.fillStyle = paddle1.color;
    ctx.fillRect(paddle1.x, paddle1.y, paddle1.w, paddle1.h);

    // Raquete 2
    ctx.shadowColor = paddle2.color;
    ctx.fillStyle = paddle2.color;
    ctx.fillRect(paddle2.x, paddle2.y, paddle2.w, paddle2.h);

    // Bola
    ctx.shadowColor = ball.color;
    ctx.shadowBlur = 20;
    ctx.fillStyle = ball.color;
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.size / 2, 0, Math.PI * 2);
    ctx.fill();

    // Reset shadow
    ctx.shadowBlur = 0;

    // Partículas
    drawParticles();

    // Linha de fundo superior/inferior
    ctx.strokeStyle = '#00ff88';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#00ff88';
    ctx.shadowBlur = 5;
    ctx.beginPath();
    ctx.moveTo(0, 1);
    ctx.lineTo(GAME_WIDTH, 1);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(0, GAME_HEIGHT - 1);
    ctx.lineTo(GAME_WIDTH, GAME_HEIGHT - 1);
    ctx.stroke();
    ctx.shadowBlur = 0;
}

// ========================================
// GAME LOOP
// ========================================
function gameLoop() {
    if (gameRunning) {
        processInput();
        updatePaddles();
        updateBall();
        updateParticles();
    }

    draw();
    requestAnimationFrame(gameLoop);
}

// ========================================
// START
// ========================================
showMessage('Pressione ESPAÇO ou toque para iniciar');
gameLoop();
