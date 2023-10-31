const button = document.getElementById("button");
const summaryElement = document.getElementById("summary");

button.addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript(
    {
      target: { tabId: tab.id },
      func: scrapeText,
    },
    async ([result]) => {
      const text = result.result;
      const summary = await getSummary(text);
      summaryElement.textContent = summary;
    }
  );
});

function scrapeText() {
  return document.body.innerText;
}

async function getSummary(text) {
    const response = await fetch("http://localhost:5000/summarize", {
        method: "POST",
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({ text }),
      });

  const data = await response.json();
  return data.summary;
}
