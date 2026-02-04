let currentSection = '';
let workoutQueue = [];
let currentExerciseIndex = 0;
let timerInterval = null;
let isPaused = false;
let currentSeconds = 0;
let isResting = false;
const REST_TIME = 120; // 2 minutes rest in seconds

// Initial exercises based on the PDF
const initialExercises = {
    warmup: [
        { name: 'Jumping Jacks', reps: 20, sets: 2, time: '', unit: 'reps' },
        { name: 'Squats', reps: '', sets: '', time: '', unit: 'reps' }
    ],
    push: [
        { name: 'Pushup', reps: 12, sets: 3, time: '', unit: 'reps' }
    ],
    pull: [
        { name: 'Australian Rows', reps: 10, sets: 2, time: '', unit: 'reps' },
        { name: 'Pull ups', reps: 8, sets: 3, time: '', unit: 'reps' }
    ],
    legs: [
        { name: 'Squats', reps: 20, sets: 3, time: '', unit: 'reps' }
    ],
    core: [
        { name: 'Plank', reps: '', sets: '', time: 1, unit: 'reps' },
        { name: 'Pull ups', reps: 8, sets: 3, time: '', unit: 'reps' }
    ],
    cooldown: [
        { name: 'Hamstring Stretches', reps: '', sets: '', time: '', unit: 'reps' }
    ]
};

// Initialize the workout
function initWorkout() {
    for (let section in initialExercises) {
        initialExercises[section].forEach(exercise => {
            renderExercise(section, exercise);
        });
    }
}

// Function to play a beep sound
function playBeep() {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800; // Frequency in Hz
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
}

function renderExercise(section, exercise) {
    const container = document.getElementById(`${section}-exercises`);
    const exerciseDiv = document.createElement('div');
    exerciseDiv.className = 'exercise-item';
    
    exerciseDiv.innerHTML = `
        <div class="exercise-name">${exercise.name}</div>
        <div class="exercise-input">
            <label>Reps</label>
            <input type="number" value="${exercise.reps}" placeholder="0">
            <span class="unit">${exercise.unit}</span>
        </div>
        <div class="exercise-input">
            <label>Sets</label>
            <input type="number" value="${exercise.sets}" placeholder="0">
            <span class="unit">sets</span>
        </div>
        <div class="exercise-input">
            <label>Time</label>
            <input type="number" value="${exercise.time}" placeholder="0">
            <span class="unit">mins</span>
        </div>
        <button class="remove-button" onclick="removeExercise(this)">Remove</button>
    `;
    
    container.appendChild(exerciseDiv);
}

function addExercise(section) {
    currentSection = section;
    document.getElementById('exerciseModal').classList.add('active');
    document.getElementById('exerciseName').focus();
}

function closeModal() {
    document.getElementById('exerciseModal').classList.remove('active');
    document.getElementById('exerciseName').value = '';
}

function confirmAddExercise() {
    const name = document.getElementById('exerciseName').value.trim();
    if (name) {
        const exercise = {
            name: name,
            reps: '',
            sets: '',
            time: '',
            unit: 'reps'
        };
        renderExercise(currentSection, exercise);
        closeModal();
    }
}

function removeExercise(button) {
    button.closest('.exercise-item').remove();
}

function beginWorkout() {
    // Build workout queue from all sections
    workoutQueue = [];
    const sections = ['warmup', 'push', 'pull', 'legs', 'core', 'cooldown'];
    
    sections.forEach(section => {
        const container = document.getElementById(`${section}-exercises`);
        const exercises = container.querySelectorAll('.exercise-item');
        
        exercises.forEach(ex => {
            const name = ex.querySelector('.exercise-name').textContent;
            const inputs = ex.querySelectorAll('input');
            const exercise = {
                name: name,
                reps: inputs[0].value || '',
                sets: inputs[1].value || '',
                time: inputs[2].value || '',
                section: section
            };
            
            // Only add exercises that have at least one value filled
            if (exercise.reps || exercise.sets || exercise.time) {
                workoutQueue.push(exercise);
            }
        });
    });
    
    if (workoutQueue.length === 0) {
        alert('Please add some exercises to your workout first!');
        return;
    }
    
    // Start the workout
    currentExerciseIndex = 0;
    document.getElementById('workoutPlayer').classList.add('active');
    loadExercise(currentExerciseIndex);
}

function loadExercise(index) {
    if (index >= workoutQueue.length) {
        completeWorkout();
        return;
    }
    
    const exercise = workoutQueue[index];
    
    // Update exercise info
    document.getElementById('playerExerciseName').textContent = exercise.name;
    document.getElementById('playerReps').textContent = exercise.reps || '--';
    document.getElementById('playerSets').textContent = exercise.sets || '--';
    document.getElementById('playerTime').textContent = exercise.time ? `${exercise.time} min` : '--';
    
    // Check if this is a time-based exercise
    const isTimeBased = exercise.time && parseInt(exercise.time) > 0;
    
    if (isTimeBased) {
        // Show timer display (Slide B)
        document.getElementById('timerDisplay').classList.add('active');
        document.querySelector('.exercise-stats').style.display = 'none';
        
        // Convert minutes to seconds for countdown timer
        currentSeconds = parseInt(exercise.time) * 60;
        updateTimerDisplay();
        startTimer();
    } else {
        // Show stats display (Slide A)
        document.getElementById('timerDisplay').classList.remove('active');
        document.querySelector('.exercise-stats').style.display = 'grid';
        
        // Stop any running timer
        stopTimer();
    }
    
    // Reset pause state and resting flag
    isPaused = false;
    isResting = false;
    updatePauseButton();
}

function startRestPeriod() {
    isResting = true;
    
    // Update display for rest period
    document.getElementById('playerExerciseName').textContent = 'Rest Period';
    document.getElementById('playerReps').textContent = '--';
    document.getElementById('playerSets').textContent = '--';
    document.getElementById('playerTime').textContent = '2 min';
    
    // Show timer display
    document.getElementById('timerDisplay').classList.add('active');
    document.querySelector('.exercise-stats').style.display = 'none';
    
    // Set 2-minute rest
    currentSeconds = REST_TIME;
    updateTimerDisplay();
    startTimer();
    
    // Reset pause state
    isPaused = false;
    updatePauseButton();
}

function startTimer() {
    stopTimer(); // Clear any existing timer
    
    timerInterval = setInterval(() => {
        if (!isPaused && currentSeconds > 0) {
            currentSeconds--;
            updateTimerDisplay();
            
            if (currentSeconds === 0) {
                stopTimer();
                playBeep(); // Play beep sound when timer ends
                
                if (isResting) {
                    // Rest is over, move to next exercise
                    setTimeout(() => {
                        currentExerciseIndex++;
                        loadExercise(currentExerciseIndex);
                    }, 1000);
                } else {
                    // Exercise is over, check if we need rest before next exercise
                    if (currentExerciseIndex < workoutQueue.length - 1) {
                        // Not the last exercise, start rest period
                        setTimeout(() => {
                            startRestPeriod();
                        }, 1000);
                    } else {
                        // Last exercise, complete workout
                        setTimeout(() => {
                            completeWorkout();
                        }, 1000);
                    }
                }
            }
        }
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimerDisplay() {
    const hours = Math.floor(currentSeconds / 3600);
    const minutes = Math.floor((currentSeconds % 3600) / 60);
    const seconds = currentSeconds % 60;
    
    const timeString = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timerClock').textContent = timeString;
}

function togglePause() {
    isPaused = !isPaused;
    updatePauseButton();
}

function updatePauseButton() {
    const pauseBtn = document.getElementById('pauseBtn');
    const svg = pauseBtn.querySelector('svg');
    const label = pauseBtn.querySelector('.control-label');
    
    if (isPaused) {
        // Show play icon
        svg.innerHTML = '<polygon points="5 3 19 12 5 21 5 3" fill="currentColor"/>';
        label.textContent = 'Resume';
    } else {
        // Show pause icon
        svg.innerHTML = '<rect x="6" y="4" width="4" height="16" rx="1" fill="currentColor"/><rect x="14" y="4" width="4" height="16" rx="1" fill="currentColor"/>';
        label.textContent = 'Pause';
    }
}

function restartExercise() {
    if (isResting) {
        startRestPeriod();
    } else {
        loadExercise(currentExerciseIndex);
    }
}

function nextExercise() {
    if (isResting) {
        // If currently resting, skip to next exercise
        currentExerciseIndex++;
        loadExercise(currentExerciseIndex);
    } else {
        // If in an exercise, check if we should rest
        if (currentExerciseIndex < workoutQueue.length - 1) {
            // Not the last exercise, start rest period
            startRestPeriod();
        } else {
            // Last exercise, complete workout
            completeWorkout();
        }
    }
}

function exitWorkout() {
    if (confirm('Are you sure you want to exit the workout?')) {
        stopTimer();
        document.getElementById('workoutPlayer').classList.remove('active');
        currentExerciseIndex = 0;
        workoutQueue = [];
    }
}

function completeWorkout() {
    stopTimer();
    alert('Congratulations! You completed your workout! 💪');
    document.getElementById('workoutPlayer').classList.remove('active');
    currentExerciseIndex = 0;
    workoutQueue = [];
}

// Handle Enter key in modal
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('exerciseName').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            confirmAddExercise();
        }
    });
    
    // Initialize on page load
    initWorkout();
});

