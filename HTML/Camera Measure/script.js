// Elements
const video = document.getElementById('camera');
const hiddenCanvas = document.getElementById('hiddenCanvas');
const previewCanvas = document.getElementById('previewCanvas');
const edgeCanvas = document.getElementById('edgeCanvas');
const magnifierCanvas = document.getElementById('magnifierCanvas');

const hamburger = document.getElementById('hamburger');
const sideMenu = document.getElementById('sideMenu');
const overlay = document.getElementById('overlay');
const closeMenu = document.getElementById('closeMenu');
const clearColorsBtn = document.getElementById('clearColors');
const colorList = document.getElementById('colorList');

const captureBtn = document.getElementById('captureBtn');
const saveSnapshot = document.getElementById('saveSnapshot');

const calibrateBtn = document.getElementById('calibrateBtn');
const measureBtn = document.getElementById('measureBtn');
const edgeToggle = document.getElementById('edgeToggle');
const calibInfo = document.getElementById('calibInfo');
const lastMeasure = document.getElementById('lastMeasure');

const previewCard = document.getElementById('previewCard');
const previewThumb = document.getElementById('previewThumb');
const previewHex = document.getElementById('previewHex');
const previewRGB = document.getElementById('previewRGB');
const previewCMYK = document.getElementById('previewCMYK');

let stream = null;
let cameraReady = false;

// Measurement state
let mode = null; // null | 'calibrate' | 'measure'
let calibPoints = null; // {p1:{x,y}, p2:{x,y}, realCm}
let tempPoints = []; // temporary clicked points on preview
let edgeVisible = false;

// prefer back camera
const constraints = {
  audio: false,
  video: { facingMode: { exact: "environment" } }
};

async function startCamera(){
  try {
    stream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = stream;
  } catch (err) {
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      video.srcObject = stream;
    } catch (err2) {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
      } catch (err3) {
        alert('Camera error. Allow camera and use HTTPS or localhost.');
        console.error(err3);
      }
    }
  }
}
startCamera();

// size hidden canvas when video metadata loads
video.addEventListener('loadedmetadata', () => {
  cameraReady = true;
  hiddenCanvas.width = video.videoWidth;
  hiddenCanvas.height = video.videoHeight;
  previewCanvas.width = video.videoWidth;
  previewCanvas.height = video.videoHeight;
  edgeCanvas.width = video.videoWidth;
  edgeCanvas.height = video.videoHeight;
});

// Sidebar toggle
hamburger.addEventListener('click', () => openMenu());
closeMenu?.addEventListener('click', () => closeMenuFn());
overlay.addEventListener('click', () => closeMenuFn());

function openMenu(){
  sideMenu.classList.add('open');
  overlay.hidden = false;
  sideMenu.setAttribute('aria-hidden','false');
}
function closeMenuFn(){
  sideMenu.classList.remove('open');
  sideMenu.setAttribute('aria-hidden','true');
  overlay.hidden = true;
}

// Magnifier: separate live zoom below capture button
const magCtx = magnifierCanvas.getContext('2d');
const MAG_W = magnifierCanvas.width;
const MAG_H = magnifierCanvas.height;
const MAG_ZOOM = 3; // zoom factor for magnifier

function drawLiveMagnifier(){
  if (!cameraReady) { requestAnimationFrame(drawLiveMagnifier); return; }
  const vRect = video.getBoundingClientRect();
  // center of video
  const cx = vRect.left + vRect.width/2;
  const cy = vRect.top + vRect.height/2;
  // map center to video native coords
  const coords = clientToVideoCoords(cx, cy);
  // sample area
  const sampleSize = Math.max(8, Math.round(MAG_W / MAG_ZOOM));
  const sx = Math.max(0, Math.min(video.videoWidth - sampleSize, Math.round(coords.x - sampleSize/2)));
  const sy = Math.max(0, Math.min(video.videoHeight - sampleSize, Math.round(coords.y - sampleSize/2)));
  // ensure hidden canvas has fresh frame
  const hctx = hiddenCanvas.getContext('2d');
  hctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
  magCtx.imageSmoothingEnabled = true;
  magCtx.clearRect(0,0,MAG_W,MAG_H);
  magCtx.drawImage(hiddenCanvas, sx, sy, sampleSize, sampleSize, 0, 0, MAG_W, MAG_H);
  // crosshair
  magCtx.strokeStyle = 'rgba(255,255,255,0.9)';
  magCtx.lineWidth = 2;
  magCtx.beginPath();
  magCtx.moveTo(MAG_W/2, 8);
  magCtx.lineTo(MAG_W/2, MAG_H-8);
  magCtx.moveTo(8, MAG_H/2);
  magCtx.lineTo(MAG_W-8, MAG_H/2);
  magCtx.stroke();
  requestAnimationFrame(drawLiveMagnifier);
}
requestAnimationFrame(drawLiveMagnifier);

// Capture frame (freeze)
const pCtx = previewCanvas.getContext('2d');
const edgeCtx = edgeCanvas.getContext('2d');
captureBtn.addEventListener('click', () => {
  if (!cameraReady) return alert('Camera not ready');
  // draw current video frame into hidden canvas at native res
  const hctx = hiddenCanvas.getContext('2d');
  hiddenCanvas.width = video.videoWidth; hiddenCanvas.height = video.videoHeight;
  hctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

  // copy to preview canvas for UI (same size)
  previewCanvas.width = hiddenCanvas.width; previewCanvas.height = hiddenCanvas.height;
  pCtx.drawImage(hiddenCanvas, 0, 0);
  previewCanvas.hidden = false;
  edgeCanvas.hidden = !edgeVisible; // show edge overlay only if toggled on

  // analyze colors (sample coarse subset to avoid heavy loops)
  analyzeColorsFromCanvas(hiddenCanvas);

  // update preview thumb with center crop
  updatePreviewThumb();
});

// Save snapshot as PNG
saveSnapshot.addEventListener('click', () => {
  if (previewCanvas.hidden) return alert('Capture a frame first');
  const url = previewCanvas.toDataURL('image/png');
  const a = document.createElement('a'); a.href = url; a.download = 'snapshot.png'; a.click();
});

// Color analysis: sample pixels with stride to reduce load
function analyzeColorsFromCanvas(canvas){
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  const data = ctx.getImageData(0,0,w,h).data;
  const colors = {};
  const stride = Math.max(4, Math.floor((w*h)/15000)); // sample ~15k points max
  for (let i = 0; i < data.length; i += 4*stride){
    const r = data[i], g = data[i+1], b = data[i+2];
    const hex = rgbToHex(r,g,b);
    if (!colors[hex]) colors[hex] = {r,g,b};
  }
  // add to sidebar list
  Object.keys(colors).slice(0,80).forEach(hex => addColorCard(colors[hex], hex));
  openMenu(); // open menu so user sees captured colors
}

// add color card to menu
function addColorCard(rgb, hex){
  const row = document.createElement('div'); row.className = 'color-row';
  const sw = document.createElement('div'); sw.className = 'color-swatch';
  const img = document.createElement('img'); img.className = 'color-thumb';
  // make thumbnail from sampled small area: solid fill
  const thumbCanvas = document.createElement('canvas'); thumbCanvas.width = 64; thumbCanvas.height = 64;
  const tctx = thumbCanvas.getContext('2d');
  tctx.fillStyle = hex; tctx.fillRect(0,0,64,64);
  img.src = thumbCanvas.toDataURL('image/png');
  sw.appendChild(img);

  const meta = document.createElement('div'); meta.className = 'color-meta';
  meta.innerHTML = `<div><b>${hex}</b></div>
                    <div class="meta-row">RGB: ${rgb.r}, ${rgb.g}, ${rgb.b}</div>
                    <div class="meta-row">CMYK: ${rgbToCmyk(rgb.r,rgb.g,rgb.b)}</div>`;

  // color box at right
  const box = document.createElement('div'); box.style.width='56px'; box.style.height='56px'; box.style.borderRadius='8px'; box.style.background=hex; box.style.border='1px solid rgba(0,0,0,0.04)';

  // copy on click feedback
  row.addEventListener('click', () => {
    navigator.clipboard?.writeText(hex).catch(()=>{});
    row.style.transform = 'scale(0.995)';
    setTimeout(()=>row.style.transform='',140);
  });

  row.appendChild(sw); row.appendChild(meta); row.appendChild(box);
  colorList.prepend(row);
}

// clear colors
clearColorsBtn.addEventListener('click', () => colorList.innerHTML='');

// Utility conversions
function rgbToHex(r,g,b){ return '#' + [r,g,b].map(v => v.toString(16).padStart(2,'0')).join('').toUpperCase(); }
function rgbToCmyk(r,g,b){
  const rr=r/255, gg=g/255, bb=b/255;
  const k = 1 - Math.max(rr,gg,bb);
  if (k === 1) return '0.00, 0.00, 0.00, 1.00';
  const c = ((1-rr-k)/(1-k)), m = ((1-gg-k)/(1-k)), y = ((1-bb-k)/(1-k));
  return `${c.toFixed(2)}, ${m.toFixed(2)}, ${y.toFixed(2)}, ${k.toFixed(2)}`;
}

/* ---------------- Edge detection (Sobel) ---------------- */
function computeSobel(canvas){
  const w = canvas.width, h = canvas.height;
  const ctx = canvas.getContext('2d');
  const src = ctx.getImageData(0,0,w,h);
  const dst = ctx.createImageData(w,h);
  // grayscale
  const gray = new Uint8ClampedArray(w*h);
  for (let i=0, j=0; i<src.data.length; i+=4, j++){
    const r=src.data[i], g=src.data[i+1], b=src.data[i+2];
    gray[j] = (0.299*r + 0.587*g + 0.114*b)|0;
  }
  const sobel = new Uint8ClampedArray(w*h);
  for (let y=1; y<h-1; y++){
    for (let x=1; x<w-1; x++){
      const idx = y*w + x;
      // Sobel kernels
      const gx = -gray[idx-w-1] - 2*gray[idx-1] - gray[idx+w-1] + gray[idx-w+1] + 2*gray[idx+1] + gray[idx+w+1];
      const gy = -gray[idx-w-1] - 2*gray[idx-w] - gray[idx-w+1] + gray[idx+w-1] + 2*gray[idx+w] + gray[idx+w+1];
      const gval = Math.hypot(gx, gy);
      sobel[idx] = gval > 120 ? 255 : 0; // threshold; adjustable
    }
  }
  // paint to edgeCanvas
  const out = edgeCtx.createImageData(w,h);
  for (let i=0, j=0; j<sobel.length; j++, i+=4){
    out.data[i] = out.data[i+1] = out.data[i+2] = sobel[j];
    out.data[i+3] = sobel[j] ? 220 : 0;
  }
  edgeCtx.putImageData(out, 0, 0);
}

/* --------------- Click handling on preview for calibration & measure -------------- */
function clientToVideoCoords(clientX, clientY){
  // Map client coords into video native coords respecting object-fit:cover
  const rect = video.getBoundingClientRect();
  const relX = clientX - rect.left;
  const relY = clientY - rect.top;
  const dispW = rect.width, dispH = rect.height;
  const vw = video.videoWidth, vh = video.videoHeight;
  // scale to cover
  const scale = Math.max(dispW / vw, dispH / vh);
  const sw = vw * scale, sh = vh * scale;
  const offsetX = (sw - dispW) / 2;
  const offsetY = (sh - dispH) / 2;
  const sx = relX + offsetX, sy = relY + offsetY;
  const nx = (sx / sw) * vw, ny = (sy / sh) * vh;
  return { x: Math.max(0, Math.min(vw-1, nx)), y: Math.max(0, Math.min(vh-1, ny)) };
}

previewCanvas.addEventListener('click', (ev) => {
  if (previewCanvas.hidden) return;
  const c = clientToVideoCoords(ev.clientX, ev.clientY);
  tempPoints.push(c);
  drawTempMarker(c);
  if (mode === 'calibrate' && tempPoints.length === 2){
    // compute pixel distance and ask user real length
    const p1 = tempPoints[0], p2 = tempPoints[1];
    const pxDist = Math.hypot(p2.x-p1.x, p2.y-p1.y);
    const input = prompt('Enter real-world length between these two points in centimeters (e.g. 10):');
    const real = parseFloat(input);
    if (isFinite(real) && real > 0){
      calibPoints = {p1,p2, realCm: real, pxDist};
      calibInfo.textContent = `${real} cm (px: ${pxDist.toFixed(1)})`;
      mode = null; tempPoints = [];
      clearTempMarkers();
      alert('Calibration saved. Now press Measure and pick two points to measure object length.');
    } else {
      alert('Invalid value. Calibration cancelled.');
      mode = null; tempPoints = []; clearTempMarkers();
    }
  } else if (mode === 'measure' && tempPoints.length === 2){
    const p1 = tempPoints[0], p2 = tempPoints[1];
    const pxDist = Math.hypot(p2.x-p1.x, p2.y-p1.y);
    if (!calibPoints){
      alert('No calibration set. Please calibrate first (press Calibrate).');
      mode = null; tempPoints = []; clearTempMarkers(); return;
    }
    const scaleCmPerPx = calibPoints.realCm / calibPoints.pxDist;
    const measuredCm = pxDist * scaleCmPerPx;
    lastMeasure.textContent = `${measuredCm.toFixed(2)} cm (px: ${pxDist.toFixed(1)})`;
    mode = null; tempPoints = []; clearTempMarkers();
    // show small toast-like visual
    alert(`Measured: ${measuredCm.toFixed(2)} cm`);
  }
});

// temp marker visuals drawn onto previewCanvas
const markCtx = previewCanvas.getContext('2d');
function drawTempMarker(pt){
  // draw semi-transparent circle at point on preview canvas overlay
  markCtx.save();
  markCtx.strokeStyle = 'rgba(255,200,20,0.95)';
  markCtx.lineWidth = 4;
  markCtx.beginPath();
  markCtx.arc(pt.x, pt.y, 12, 0, Math.PI*2);
  markCtx.stroke();
  markCtx.restore();
}
function clearTempMarkers(){
  // redraw preview image from hiddenCanvas to clear markers
  markCtx.drawImage(hiddenCanvas, 0, 0);
}

/* Buttons for calibration/measure/edge toggle */
calibrateBtn.addEventListener('click', () => {
  if (previewCanvas.hidden) return alert('Capture a frame first');
  mode = 'calibrate'; tempPoints = [];
  alert('Calibration mode: click two points on the preview that correspond to a known real-world length.');
});
measureBtn.addEventListener('click', () => {
  if (previewCanvas.hidden) return alert('Capture a frame first');
  mode = 'measure'; tempPoints = [];
  alert('Measure mode: click two points on the preview to measure object length.');
});
edgeToggle.addEventListener('click', () => {
  if (previewCanvas.hidden) return alert('Capture to see edges');
  edgeVisible = !edgeVisible;
  edgeCanvas.hidden = !edgeVisible;
  if (edgeVisible){
    computeSobel(hiddenCanvas);
  }
});

/* preview thumbnail update */
function updatePreviewThumb(){
  // sample center area for preview thumb & average color
  const w = hiddenCanvas.width, h = hiddenCanvas.height;
  const thumbSize = 150;
  const ctx = previewThumb.getContext('2d');
  // center crop
  const sx = Math.max(0, Math.round((w - thumbSize)/2));
  const sy = Math.max(0, Math.round((h - thumbSize)/2));
  const sctx = hiddenCanvas.getContext('2d');
  const id = sctx.getImageData(sx, sy, thumbSize, thumbSize);
  // draw scaled into previewThumb
  ctx.clearRect(0,0,previewThumb.width, previewThumb.height);
  // use offscreen small canvas
  const small = document.createElement('canvas'); small.width = thumbSize; small.height = thumbSize;
  small.getContext('2d').putImageData(id, 0, 0);
  ctx.drawImage(small, 0, 0, previewThumb.width, previewThumb.height);
  // compute average color for preview metadata
  let r=0,g=0,b=0, count = id.data.length/4;
  for (let i=0;i<id.data.length;i+=4){ r+=id.data[i]; g+=id.data[i+1]; b+=id.data[i+2]; }
  r = Math.round(r/count); g = Math.round(g/count); b = Math.round(b/count);
  const hex = rgbToHex(r,g,b);
  previewHex.textContent = hex;
  previewRGB.textContent = `RGB: (${r}, ${g}, ${b})`;
  previewCMYK.textContent = `CMYK: ${rgbToCmyk(r,g,b)}`;
  previewCard.hidden = false;
}

/* draw previewCanvas image and edge overlay when capture occurs */
function refreshPreviewAndEdges(){
  if (previewCanvas.hidden) return;
  pCtx.drawImage(hiddenCanvas, 0, 0);
  if (edgeVisible) computeSobel(hiddenCanvas);
}

/* helper: clear temp markers when user re-captures */
function clearTempState(){
  tempPoints = []; mode = null;
  // redraw preview
  refreshPreviewAndEdges();
}

/* copy previewCanvas to hiddenCanvas if needed and handle resizing */
hiddenCanvas.addEventListener('click', () => {}); // noop

// small utility: copy image to file (used when saving)
function dataURLtoBlob(dataurl) {
  const arr = dataurl.split(','), mime = arr[0].match(/:(.*?);/)[1];
  const bstr = atob(arr[1]); let n = bstr.length; const u8arr = new Uint8Array(n);
  while(n--) u8arr[n] = bstr.charCodeAt(n);
  return new Blob([u8arr], {type:mime});
}

/* clientToVideoCoords helper for preview clicks (already defined above but redeclare to ensure availability in this file scope) */
function clientToVideoCoords(clientX, clientY){
  const rect = video.getBoundingClientRect();
  const relX = clientX - rect.left;
  const relY = clientY - rect.top;
  const dispW = rect.width, dispH = rect.height;
  const vw = video.videoWidth, vh = video.videoHeight;
  const scale = Math.max(dispW / vw, dispH / vh);
  const sw = vw * scale, sh = vh * scale;
  const offsetX = (sw - dispW) / 2, offsetY = (sh - dispH) / 2;
  const sx = relX + offsetX, sy = relY + offsetY;
  const nx = (sx / sw) * vw, ny = (sy / sh) * vh;
  return { x: Math.max(0, Math.min(vw-1, nx)), y: Math.max(0, Math.min(vh-1, ny)) };
}

/* initial visibility state */
overlay.hidden = true;
previewCanvas.hidden = true;
edgeCanvas.hidden = true;
previewCard.hidden = true;

/* make sure previewCanvas draws hiddenCanvas when capture occurs (also used for clearing markers) */
function drawPreviewFromHidden(){
  if (!cameraReady) return;
  previewCanvas.width = hiddenCanvas.width;
  previewCanvas.height = hiddenCanvas.height;
  pCtx.drawImage(hiddenCanvas, 0, 0);
}