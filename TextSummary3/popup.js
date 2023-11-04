document.addEventListener('DOMContentLoaded', function () {
  var button = document.getElementById('button');
  var summaryBox = document.getElementById('summary');

  button.addEventListener('click', function () {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      var url = tabs[0].url;

      if (url.includes('youtube.com')) {
        // Pass the YouTube video URL to your local Flask server for transcription
        fetch('http://localhost:5000/transcribe', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url: url }),
        })
          .then((response) => response.json())
          .then((transcriptionData) => {
            // Assuming transcriptionData contains the video transcript

            // Pass the transcript to your local Flask server for summarization
            fetch('http://localhost:5000/summarize', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({ transcript: transcriptionData.transcript }),
            })
              .then((response) => response.json())
              .then((summaryData) => {
                // Assuming summaryData contains the summarized text

                // Display the summary in the summary box
                summaryBox.textContent = summaryData.summary;

                // Generate a PDF from the summary and provide a download link
                generatePDF(summaryData.summary);
              })
              .catch((error) => {
                console.error('Error:', error);
                summaryBox.textContent = 'An error occurred while processing the video.';
              });
          })
          .catch((error) => {
            console.error('Error:', error);
            summaryBox.textContent = 'An error occurred while processing the video.';
          });
      } else {
        summaryBox.textContent = 'This is not a YouTube video page.';
      }
    });
  });

  function generatePDF(summaryText) {
    const pdfContent = `data:application/pdf;base64,${btoa(summaryText)}`;

    // Create a download link for the PDF
    const downloadLink = document.createElement('a');
    downloadLink.href = pdfContent;
    downloadLink.download = 'summary.pdf';
    downloadLink.textContent = 'Download PDF';

    // Append the link to the document
    document.body.appendChild(downloadLink);
  }
});
