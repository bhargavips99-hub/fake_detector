async function analyzeNews() {

    const text =
        document.getElementById(
            "newsInput"
        ).value.trim();

    if (!text) {

        alert(
            "Please enter news text."
        );

        return;
    }

    document
        .getElementById("loading")
        .classList.remove("hidden");

    document
        .getElementById("resultCard")
        .classList.add("hidden");

    try {

        const response =
    await fetch(
        "http://192.168.50.117:5000/api/analyze",
                
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                        "application/json"
                    },

                    body:JSON.stringify({
                        text:text
                    })
                }
            );

        const data =
            await response.json();

        document
            .getElementById("loading")
            .classList.add("hidden");

        if(!data.success){

            alert(data.error);
            return;
        }

        const prediction =
            document.getElementById(
                "prediction"
            );

        prediction.innerText =
            data.prediction;

        prediction.className = "";

        if(
            data.prediction ===
            "Likely Reliable"
        ){

            prediction.classList.add(
                "reliable"
            );
        }
        else if(
            data.prediction ===
            "Likely Misleading"
        ){

            prediction.classList.add(
                "fake"
            );
        }
        else{

            prediction.classList.add(
                "verify"
            );
        }

        document.getElementById(
            "confidence"
        ).innerText =
            data.confidence + "%";

        document.getElementById(
            "trustScore"
        ).innerText =
            data.trust_score + "/100";

        loadList(
            "clickbaitWords",
            data.clickbait_words
        );

        loadList(
            "warnings",
            data.warning_signals
        );

        loadList(
            "explanation",
            data.explanation
        );

        document.getElementById(
            "disclaimer"
        ).innerText =
            data.disclaimer;

        document
            .getElementById(
                "resultCard"
            )
            .classList.remove(
                "hidden"
            );

    }
    catch(error){

        console.error(error);

        alert(
            "Server error occurred."
        );
    }
}

function loadList(
    elementId,
    items
){

    const list =
        document.getElementById(
            elementId
        );

    list.innerHTML = "";

    if(
        !items ||
        items.length === 0
    ){

        const li =
            document.createElement(
                "li"
            );

        li.textContent =
            "None";

        list.appendChild(li);

        return;
    }

    items.forEach(item => {

        const li =
            document.createElement(
                "li"
            );

        li.textContent = item;

        list.appendChild(li);
    });
}