import csv
import random
import copy
import json

def load_data(filename):
    pairs = []
    try:
        with open(filename, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                pairs.append((row['List-I'], row['List-II']))
    except:
        return []
    return pairs

def format_matching_string(roman_mapping):
    roman_numerals = ["I", "II", "III", "IV"]
    parts = [f"{char}-{roman_numerals[roman_mapping[char]]}" for char in sorted(roman_mapping.keys())]
    return ", ".join(parts)

def generate_distractors(correct_mapping):
    distractors = []
    letters = "ABCD"
    while len(distractors) < 3:
        indices = list(range(4))
        random.shuffle(indices)
        mapping = {letters[i]: indices[i] for i in range(4)}
        if mapping != correct_mapping and mapping not in distractors:
            distractors.append(format_matching_string(mapping))
    return distractors

def generate_web_quiz(csv_file, output_html, num_questions=20):
    data = load_data(csv_file)
    if not data:
        print("CSV missing or empty.")
        return

    questions_data = []
    for q_num in range(1, num_questions + 1):
        if len(data) < 4: break
        sample = random.sample(data, 4)
        list_i = [item[0] for item in sample]
        pairs_dict = dict(sample)
        
        list_ii_vals = [pairs_dict[item] for item in list_i]
        list_ii_display = copy.deepcopy(list_ii_vals)
        while True:
            random.shuffle(list_ii_display)
            if all(list_ii_display[j] != list_ii_vals[j] for j in range(4)): break

        correct_map = {"ABCD"[j]: list_ii_display.index(pairs_dict[list_i[j]]) for j in range(4)}
        correct_text = format_matching_string(correct_map)
        options = [correct_text] + generate_distractors(correct_map)
        random.shuffle(options)
        
        questions_data.append({
            "id": q_num,
            "list_i": list_i,
            "list_ii": list_ii_display,
            "options": options,
            "answer": options.index(correct_text) + 1
        })

    # Google Quiz Schema
    schema_json = json.dumps({
        "@context": "https://schema.org",
        "@type": "Quiz",
        "name": "Physics Dimensional Analysis Quiz",
        "hasPart": [{"@type": "Question", "name": f"Match Set {q['id']}"} for q in questions_data]
    })

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JEE Match the Following Questions</title>
    
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.45/dist/katex.min.css" integrity="sha384-UA8juhPf75SzzAMA/4fo3yOU7sBJ0om7SCD2GHq0fZqZco6tr1UCV7nUbk9J90JM" crossorigin="anonymous">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.45/dist/katex.min.js" integrity="sha384-Tt7wBxLKwSzFVRET4O4U9H6v8MNaQ/CjN2FMP4xFm0ErrFu6aNqoonRVW5W40iGI" crossorigin="anonymous"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.45/dist/contrib/auto-render.min.js" integrity="sha384-bjyGPfbij8/NDKJhSGZNP/khQVgtHUE5exjm4Ydllo42FwIgYsdLO2lXGmRBf5Mz" crossorigin="anonymous"
    onload="renderMathInElement(document.body);"></script>

    <style>
        :root {{
            --bg: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
            --glass: rgba(255, 255, 255, 0.1);
            --border: rgba(255, 255, 255, 0.1);
            --text: #f8fafc;
        }}

        @media (prefers-color-scheme: light) {{
            :root {{
                --bg: linear-gradient(135deg, #f8fafc 0%, #dbeafe 100%);
                --glass: rgba(255, 255, 255, 0.7);
                --border: rgba(0, 0, 0, 0.1);
                --text: #0f172a;
            }}
        }}

        body {{
            font-family: 'Inter', system-ui, sans-serif;
            background: var(--bg);
            background-attachment: fixed;
            color: var(--text);
            margin: 0;
            padding: clamp(10px, 5vw, 40px);
            display: flex;
            flex-direction: column;
            align-items: center;
            font-size: 1.25rem;
        }}

        .container {{ width: 100%; max-width: 850px; }}
        h1 {{ font-size: 3rem; text-align: center; margin-bottom: 50px; font-weight: 800; letter-spacing: -0.05em; }}

        .glass-card {{
            background: var(--glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            border-radius: 32px;
            padding: clamp(20px, 5vw, 40px);
            margin-bottom: 50px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }}

        table {{ width: 100%; border-collapse: separate; border-spacing: 0; margin: 30px 0; border-radius: 20px; overflow: hidden; border: 1px solid var(--border); }}
        th, td {{ padding: 20px; text-align: left; border-bottom: 1px solid var(--border); font-size: 1.2rem; }}
        th {{ background: rgba(0,0,0,0.05); font-weight: 700; text-transform: uppercase; font-size: 0.9rem; letter-spacing: 0.1em; }}

        .options-container {{ display: grid; gap: 15px; margin-top: 30px; }}
        .opt-btn {{
            background: rgba(255,255,255,0.05);
            border: 1px solid var(--border);
            padding: 20px;
            border-radius: 18px;
            color: inherit;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 1.15rem;
            text-align: left;
        }}
        .opt-btn:hover:not(:disabled) {{ background: rgba(255,255,255,0.15); transform: translateY(-2px); }}
        .opt-btn.correct {{ background: #10b981 !important; border-color: #10b981; color: white !important; font-weight: bold; }}
        .opt-btn.wrong {{ background: #ef4444 !important; border-color: #ef4444; color: white !important; font-weight: bold; }}

        .feedback {{ font-weight: 700; margin-top: 25px; text-align: center; font-size: 1.4rem; min-height: 1.5em; }}
        
        @media (max-width: 600px) {{
            h1 {{ font-size: 2rem; }}
            .glass-card {{ padding: 20px; }}
            th, td {{ padding: 12px; font-size: 1rem; }}
            .opt-btn {{ font-size: 1rem; padding: 15px; }}
        }}
    </style>

    <script type="application/ld+json">{schema_json}</script>
</head>
<body>
    <div class="container">
        <h1>Dimensional Alanysis Match the following questions for JEE</h1>
        <div id="quiz-root"></div>
    </div>

    <!-- RAW JSON to preserve backslashes -->
    <script id="quiz-data" type="application/json">
        {json.dumps(questions_data)}
    </script>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            const quizData = JSON.parse(document.getElementById('quiz-data').textContent);
            const root = document.getElementById('quiz-root');
            const letters = ["A", "B", "C", "D"];
            const romans = ["I", "II", "III", "IV"];

            quizData.forEach(q => {{
                const card = document.createElement('div');
                card.className = 'glass-card';

                let rows = '';
                for(let i=0; i<4; i++) {{
                    rows += `<tr>
                        <td><strong>${{letters[i]}}.</strong> ${{q.list_i[i]}}</td>
                        <td><strong>${{romans[i]}}.</strong> $${{q.list_ii[i]}}$</td>
                    </tr>`;
                }}

                card.innerHTML = `
                    <h3 style="margin-top:0">Question ${{q.id}}: Match List I with list II</h3>
                    <table>
                        <thead><tr><th>List-I</th><th>List-II</th></tr></thead>
                        <tbody>${{rows}}</tbody>
                    </table>
                    <div class="options-container" id="opts-${{q.id}}">
                        ${{q.options.map((opt, i) => `
                            <button class="opt-btn" onclick="checkAnswer(this, ${{q.id}}, ${{i+1}}, ${{q.answer}})">
                                (${{i+1}}) ${{opt}}
                            </button>
                        `).join('')}}
                    </div>
                    <div id="msg-${{q.id}}" class="feedback"></div>
                `;
                root.appendChild(card);
            }});

            // Manual KaTeX trigger
            if (window.renderMathInElement) {{
                renderMathInElement(document.body, {{
                    delimiters: [
                        {{left: '$$', right: '$$', display: true}},
                        {{left: '$', right: '$', display: false}}
                    ],
                    throwOnError: false
                }});
            }}
        }});

        function checkAnswer(btn, qId, selected, correct) {{
            const container = document.getElementById('opts-' + qId);
            const msg = document.getElementById('msg-' + qId);
            const buttons = container.querySelectorAll('.opt-btn');
            
            buttons.forEach(b => b.disabled = true);

            if(selected === correct) {{
                btn.classList.add('correct');
                msg.innerHTML = "✨ Correct!";
                msg.style.color = "#10b981";
            }} else {{
                btn.classList.add('wrong');
                buttons[correct-1].classList.add('correct');
                msg.innerHTML = "❌ Incorrect. Option (" + correct + ") is correct.";
                msg.style.color = "#ef4444";
            }}
        }}
    </script>
</body>
</html>"""

    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Quiz exported to: {output_html}")

generate_web_quiz("data.csv", "physics_quiz.html")