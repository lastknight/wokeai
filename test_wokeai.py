import pandas as pd
import os
import json
import sys
from datetime import date
from openai import OpenAI

# Initialize OpenAI client with API key from environment variable
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    print("Error: OPENAI_API_KEY environment variable not set.")
    sys.exit(1)

client = OpenAI(api_key=api_key)

def generate_llm_response(prompt, model):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Error generating response"

def load_questions_from_excel(file_path):
    sheets = ['pride', 'guilt', 'jelousy', 'shame', 'empathy']
    all_questions = []
    
    for sheet in sheets:
        df = pd.read_excel(file_path, sheet_name=sheet)
        questions = df.to_dict('records')
        all_questions.extend(questions)
    
    return all_questions

def is_correct_response(actual, expected):
    return any(word.lower() in actual.lower() for word in expected.lower().split())

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <excel_file_path> <model>")
        sys.exit(1)
    
    excel_file_path = sys.argv[1]
    model = sys.argv[2]
    
    if os.path.exists(excel_file_path):
        print("Excel file found!")
        questions = load_questions_from_excel(excel_file_path)
        print(f"Total number of questions loaded: {len(questions)}")
        
        results = []
        for i, q in enumerate(questions):
            print(f"\nQuestion {i+1}:")
            print(f"Input: {q['Statement']}")
            actual_output = generate_llm_response(q['Statement'], model)
            print(f"Model's response: {actual_output}")
            print(f"Expected response: {q['Expected']}")
            
            is_correct = is_correct_response(actual_output, q['Expected'])
            print(f"Correct: {'Yes' if is_correct else 'No'}")
            
            results.append({
                "statement": q['Statement'],
                "expected": q['Expected'],
                "actual": actual_output,
                "correct": is_correct
            })
        
        correct_count = sum(r['correct'] for r in results)
        print(f"\nFinal result: {correct_count}/{len(questions)} correct answers")

        # Save results to JSON
        today = date.today().strftime("%Y%m%d")
        filename = f"{today} - {model}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=4)
        
        print(f"Results saved to {filename}")
    else:
        print("Excel file not found. Check the file name and location.")
