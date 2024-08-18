document.getElementById('upload').addEventListener('click', (event) => {
    if (localStorage.getItem('videoUploaded') === 'true') {
        localStorage.removeItem('videoUploaded');
        location.reload();
    }
});

document.getElementById('upload').addEventListener('change', async (event) => {
    const file = event.target.files[0];
    if (!file) {
        alert('No file selected');
        return;
    }

    localStorage.setItem('videoUploaded', 'true');

    const formData = new FormData();
    formData.append('video', file);

    try {
        const response = await fetch('/upload_video', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to upload video');
        }

        const framesData = await response.json();
        displayFrames(framesData);
    } catch (error) {
        console.error('Error uploading video:', error);
        alert(error.message);
    }
});

function displayFrames(framesData) {
    let index = 0;
    const interval = setInterval(() => {
        if (index >= framesData.length) {
            clearInterval(interval);
            return;
        }

        const frameData = framesData[index];
        document.getElementById('output').src = `data:image/jpeg;base64,${frameData.image}`;
        document.getElementById('poseLabel').innerText = `Pose: ${frameData.label}`;
        document.getElementById('poseLabel').style.color = 
            frameData.label.includes('Move inside the camera') ? 'black' : 
            frameData.label.includes('Incorrect') ? 'red' : 'green';
        document.getElementById('counter').innerText = `Counter: ${frameData.counter}`;
        document.getElementById('stage').innerText = `Current stage: ${frameData.stage}`;
        
        const anglesStatusElement = document.getElementById('anglesStatus');
        anglesStatusElement.innerHTML = `Joints status: <br> ${frameData.angles_status.map(status => {
            const color = status.includes('Unknown') ? 'black' : 
                          status.includes('Incorrect') ? 'red' : 'green';
            return `<span style="color: ${color}">${status}</span>`;
        }).join('<br>')}`;
        
        document.getElementById('detailedFeedback').innerText = `Feedback: ${frameData.detailed_feedback.join(', ')}`;

        index++;
    }, 100);  // Adjust the interval to control the frame rate
}


document.getElementById('startCamera').addEventListener('click', async () => {

    if (localStorage.getItem('videoUploaded') === 'true') {
        location.reload();
        localStorage.removeItem('videoUploaded');
    }

    const video = document.getElementById('camera');
    const startCameraButton = document.getElementById('startCamera');
    video.style.display = 'none';
    startCameraButton.style.backgroundColor = 'red';
    if (startCameraButton.innerText === 'Start Camera') {

        try {
            const resetResponse = await fetch('/reset_pipeline', { method: 'POST' });

            if (!resetResponse.ok) {
                throw new Error('Failed to reset the pipeline');
            }

            video.style.display = 'block';
            startCameraButton.innerText = 'Stop Camera';

            const selectedCameraId = document.getElementById('cameraSelect').value;
            const constraints = {
                video: { deviceId: selectedCameraId ? { exact: selectedCameraId } : undefined }
            };

            navigator.mediaDevices.getUserMedia(constraints).then(stream => {
                video.srcObject = stream;
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');

                window.cameraInterval = setInterval(async () => {
                    const desiredWidth = 500;
                    const desiredHeight = 375;

                    canvas.width = desiredWidth;
                    canvas.height = desiredHeight;

                    ctx.drawImage(video, 0, 0, desiredWidth, desiredHeight);
                    const frame = canvas.toDataURL('image/jpeg', 0.5);

                    try {
                        const response = await fetch('/process_camera', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ frame })
                        });

                        if (!response.ok) {
                            throw new Error('Failed to process camera frame');
                        }

                        const data = await response.json();
                        updateUI(data);
                    } catch (error) {
                        console.error('Error processing camera frame:', error);
                        alert('Failed to process camera frame. Please try again.');
                    }
                }, 100);
            }).catch(error => {
                console.error('Error accessing the camera:', error);
                alert('Failed to access the camera. Please check your device settings.');
            });
        } catch (error) {
            console.error('Error resetting the pipeline:', error);
            alert('Failed to reset the pipeline. Please try again.');
        }
    } else {
        clearInterval(window.cameraInterval);
        video.srcObject.getTracks().forEach(track => track.stop());
        video.style.display = 'none';
        startCameraButton.innerText = 'Start Camera';
        startCameraButton.style.backgroundColor = 'green';
        clearUI();
    }
});

function updateUI(data) {
    document.getElementById('output').src = `data:image/jpeg;base64,${data.image}`;
    document.getElementById('poseLabel').innerText = ` ${data.label}`;
    document.getElementById('poseLabel').style.color = data.label.includes('Move inside the camera') ? 'black' : 
        data.label.includes('Incorrect') ? 'red' : 'green';
    document.getElementById('counter').innerText = `Counter: ${data.counter}`;
    document.getElementById('stage').innerText = `Current stage: ${data.stage}`;
    const anglesStatusElement = document.getElementById('anglesStatus');
    anglesStatusElement.innerHTML = `Joints status: <br> ${data.angles_status.map(status => {
        const color = status.includes('Unknown') ? 'black' : 
                      status.includes('Incorrect') ? 'red' : 'green';
        return `<span style="color: ${color}">${status}</span>`;
    }).join('<br>')}`;
    document.getElementById('detailedFeedback').innerText = `Feedback: ${data.detailed_feedback.join(', ')}`;
}

function clearUI() {
    document.getElementById('output').src = '';
    document.getElementById('poseLabel').innerText = '';
    document.getElementById('counter').innerText = '';
    document.getElementById('stage').innerText = '';
    document.getElementById('anglesStatus').innerHTML = '';
    document.getElementById('detailedFeedback').innerText = '';
}

async function populateCameraOptions() {
    const videoInputSelect = document.getElementById('cameraSelect');
    const devices = await navigator.mediaDevices.enumerateDevices();

    devices.forEach(device => {
        if (device.kind === 'videoinput') {
            const option = document.createElement('option');
            option.value = device.deviceId;
            option.text = device.label || `Camera ${videoInputSelect.length + 1}`;
            videoInputSelect.add(option);
        }
    });
}

populateCameraOptions();
