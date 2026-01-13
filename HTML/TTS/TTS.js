const synth = window.speechSynthesis;
const voiceSelect = document.getElementById('voiceSelect');
const textInput = document.getElementById('textInput');
const speakBtn = document.getElementById('speakBtn');
const stopBtn = document.getElementById('stopBtn');
const saveBtn = document.getElementById('saveBtn');

let voices = [];

function populateVoices() {
  voices = synth.getVoices();
  voiceSelect.innerHTML = '';
  voices.forEach((voice, i) => {
    const option = document.createElement('option');
    option.value = i;
    option.textContent = `${voice.name} (${voice.lang})${voice.default ? ' [default]' : ''}`;
    voiceSelect.appendChild(option);
  });
}

// Chrome loads voices asynchronously
synth.onvoiceschanged = populateVoices;

speakBtn.addEventListener('click', () => {
  if (synth.speaking) synth.cancel();

  const utterance = new SpeechSynthesisUtterance(textInput.value);
  const selectedVoice = voices[voiceSelect.value];
  utterance.voice = selectedVoice;

  synth.speak(utterance);
});

stopBtn.addEventListener('click', () => {
  synth.cancel();
});

// Save as audio using SpeechSynthesisRecorder (browser does NOT natively support this)
// Workaround: Save text to file instead
saveBtn.addEventListener('click', () => {
  const blob = new Blob([textInput.value], { type: 'text/plain' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'speech.txt';
  a.click();
});
