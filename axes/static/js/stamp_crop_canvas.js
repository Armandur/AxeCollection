// Funktion för att skapa beskurna stämpelbilder med canvas
function createCroppedStampImages() {
    const stampCards = document.querySelectorAll('.stamp-crop-container img[data-stamp-width]');

    stampCards.forEach((img) => {
        const stampWidth = parseFloat(img.dataset.stampWidth);
        const stampHeight = parseFloat(img.dataset.stampHeight);
        const cropX = parseFloat(img.dataset.cropX);
        const cropY = parseFloat(img.dataset.cropY);

        if (stampWidth && stampHeight && cropX !== null && cropY !== null) {
            // Kontrollera om bilden redan har beskärts (har data: URL)
            if (img.src.startsWith('data:')) {
                return;
            }
            
            const canvasImage = new Image();
            canvasImage.crossOrigin = 'anonymous';

            canvasImage.onload = function() {
                const pixelX = Math.round((cropX / 100) * this.width);
                const pixelY = Math.round((cropY / 100) * this.height);
                const pixelWidth = Math.round((stampWidth / 100) * this.width);
                const pixelHeight = Math.round((stampHeight / 100) * this.height);

                try {
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    canvas.width = pixelWidth;
                    canvas.height = pixelHeight;
                    ctx.drawImage(this, pixelX, pixelY, pixelWidth, pixelHeight, 0, 0, pixelWidth, pixelHeight);
                    const croppedImageUrl = canvas.toDataURL('image/jpeg', 0.9);
                    
                    img.src = croppedImageUrl;
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.objectFit = 'contain';
                    img.style.objectPosition = 'center';
                } catch (error) {
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.objectFit = 'contain';
                    img.style.objectPosition = `-${cropX}% -${cropY}%`;
                }
            };

            canvasImage.onerror = function() {
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.objectFit = 'contain';
                img.style.objectPosition = `-${cropX}% -${cropY}%`;
            };

            canvasImage.src = img.src;
        }
    });
}

// Kör funktionen när DOM är redo
document.addEventListener('DOMContentLoaded', function() {
    createCroppedStampImages();
}); 