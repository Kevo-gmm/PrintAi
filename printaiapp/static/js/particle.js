// select the canvas element and the carousel element
const canvas = document.querySelector("#firework-canvas");
const carousel = document.querySelector("#myCarousel");

// set the canvas size to match the size of the carousel
canvas.width = carousel.offsetWidth;
canvas.height = carousel.offsetHeight;

// get the canvas context
const ctx = canvas.getContext("2d");

// define the particle properties
const particleCount = 100; // number of particles
const particleSize = 3; // size of each particle
const particleSpeed = 1; // speed of each particle
const particleOpacity = 1; // initial opacity of each particle
const particleFade = 0.01; // amount by which the particle's opacity decreases per frame
const particleHue = 0; // initial hue of each particle (color)
const particleSaturation = 100; // initial saturation of each particle (color)
const particleLightness = 50; // initial lightness of each particle (color)
const particleBlur = 10; // amount of blur applied to each particle

// create an array to store the particles
const particles = [];

// define the particle class
class Particle {
  constructor(x, y, directionX, directionY) {
    this.x = x;
    this.y = y;
    this.directionX = directionX;
    this.directionY = directionY;
    this.size = particleSize;
    this.opacity = particleOpacity;
    this.color = `hsla(${particleHue}, ${particleSaturation}%, ${particleLightness}%, ${this.opacity})`;
    this.blur = particleBlur;
  }

  // method to update the particle's position and decrease its opacity
  update() {
    // update the position of the particle
    this.x += this.directionX;
    this.y += this.directionY;
    // decrease the particle's opacity
    this.opacity -= particleFade;

    // if the particle is off the screen, remove it from the particles array
    if (this.opacity < 0) {
      particles.splice(particles.indexOf(this), 1);
    }

    // update the particle's color
    this.color = `hsla(${particleHue}, ${particleSaturation}%, ${particleLightness}%, ${this.opacity})`;
  }

  // method to draw the particle on the canvas
  draw() {
    ctx.fillStyle = this.color;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
    ctx.closePath();
    ctx.fill();
  }
}

// function to create the particles
function createParticles() {
  // get the center point of the carousel
  const centerX = carousel.offsetWidth / 2;
  const centerY = carousel.offsetHeight / 2;
  // generate random angles
  const angle = Math.random() * 360;
  const angleRadians = (angle * Math.PI) / 180;
  // generate random distances from the center
  const distance = Math.random() * 50;
  // calculate the starting position of the particle
  const x = centerX + Math.cos(angleRadians) * distance;
  const y = centerY + Math.sin(angleRadians) * distance;
  // calculate the direction of the particle
  const directionX = Math.cos(angleRadians) * particleSpeed;
  const directionY = Math.sin(angleRadians) * particleSpeed;
  // create a new particle
  const particle = new Particle(x, y, directionX, directionY);
  // add the particle to the particles array
  particles.push(particle);
}

// function to update and draw the particles
function updateAndDrawParticles() {
  // clear the canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // iterate through the particles array
  for (let i = 0; i < particles.length; i++) {
    // update and draw the particle
    particles[i].update();
    particles[i].draw();
  }

  // if there are fewer than the desired number of particles, create more
  if (particles.length < particleCount) {
    createParticles();
  }
}

// animate the particles
function animate() {
  updateAndDrawParticles();
  requestAnimationFrame(animate);
}

// start the animation
animate();
