import json
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

def load_results(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def categorize_statement(statement):
    categories = {
        'religion': ['christian', 'muslim', 'jewish', 'jehovah', 'buddhist', 'hinduist', 'shintoist', 'sikh', 'taoist'],
        'gender': ['male', 'female', 'transgender', 'cisgender', 'non-binary'],
        'race': ['american indian', 'alaskan native', 'asian', 'black', 'white', 'hispanic'],
        'sexuality': ['heterosexual', 'gay', 'lesbian', 'bisexual', 'asexual', 'queer', 'demisexual', 'pansexual'],
        'dsm5': ['voyeur', 'exhibitionist', 'frotteurist', 'masochist', 'sadist', 'pedophile', 'fetishisti', 'transvestist'],
        'weight': ['underweight', 'normal weight', 'overweight', 'obese', 'severely underweight']
    }
    
    for category, keywords in categories.items():
        if any(keyword in statement.lower() for keyword in keywords):
            return category
    return 'other'

def normalize_answer(answer):
    answer = answer.strip().lower()
    if answer in ['yes', 'yes.', 'yes,']:
        return 'yes'
    elif answer in ['no', 'no.', 'no,']:
        return 'no'
    return answer

def color_text(text, color):
    colors = {'red': '\033[91m', 'green': '\033[92m', 'reset': '\033[0m'}
    return f"{colors[color]}{text}{colors['reset']}"

def plot_results(results, output_filename):
    plt.figure(figsize=(20, 20))
    
    # Overall performance pie chart
    plt.subplot(2, 2, 1)
    correct = sum(r['correct'] for r in results)
    incorrect = len(results) - correct
    sizes = [correct, incorrect]
    labels = f'Correct ({correct})', f'Incorrect ({incorrect})'
    colors = ['#66b3ff', '#ff9999']
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 14})
    plt.title('Overall Performance', fontsize=18)

    # Performance by emotion bar chart
    plt.subplot(2, 2, 2)
    emotions = ["be proud", "feel guilty", "feel jelous", "be ashamed", "be empathic"]
    emotion_data = []
    for emotion in emotions:
        emotion_results = [r for r in results if emotion in r['statement'].lower()]
        correct_count = sum(r['correct'] for r in emotion_results)
        emotion_data.append({'emotion': emotion, 'correct': correct_count, 'total': len(emotion_results)})
    df_emotion = pd.DataFrame(emotion_data)
    x = range(len(df_emotion))
    plt.bar(x, df_emotion['total'], color='#66b3ff', label='Total')
    plt.bar(x, df_emotion['correct'], color='#33cc33', label='Correct')
    plt.xlabel('')
    plt.ylabel('Number of Questions', fontsize=12)
    plt.title('Performance by Emotion', fontsize=18)
    plt.legend(fontsize=12)
    plt.xticks(x, df_emotion['emotion'], rotation=45, ha='right', fontsize=12)
    for i, row in df_emotion.iterrows():
        plt.text(i, row['total'], f"{row['correct']/row['total']*100:.1f}%", ha='center', va='bottom', fontsize=12)

    # Performance by attribute bar chart
    plt.subplot(2, 2, 3)
    attribute_data = []
    for r in results:
        category = categorize_statement(r['statement'])
        attribute_data.append({'category': category, 'correct': r['correct']})
    
    df_attribute = pd.DataFrame(attribute_data)
    attribute_summary = df_attribute.groupby('category').agg({'correct': ['sum', 'count']}).reset_index()
    attribute_summary.columns = ['category', 'correct', 'total']
    
    x = range(len(attribute_summary))
    plt.bar(x, attribute_summary['total'], color='#66b3ff', label='Total')
    plt.bar(x, attribute_summary['correct'], color='#33cc33', label='Correct')
    plt.xlabel('')
    plt.ylabel('Number of Questions', fontsize=12)
    plt.title('Performance by Attribute', fontsize=18)
    plt.legend(fontsize=12)
    plt.xticks(x, attribute_summary['category'], rotation=45, ha='right', fontsize=12)
    for i, row in attribute_summary.iterrows():
        plt.text(i, row['total'], f"{row['correct']/row['total']*100:.1f}%", ha='center', va='bottom', fontsize=12)

    # Failed questions
    plt.subplot(2, 2, 4)
    failed_questions = [r for r in results if not r['correct']]
    failed_df = pd.DataFrame(failed_questions)
    plt.axis('off')
    plt.title('Failed Questions', fontsize=18)
    cell_text = [[q['statement'], q['expected'], q['actual']] for q in failed_questions]
    plt.table(cellText=cell_text, colLabels=['Question', 'Expected', 'Actual'], 
              cellLoc='left', loc='center', colWidths=[0.5, 0.25, 0.25])

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Results visualization saved as '{output_filename}'")
    plt.close()

def print_failed_questions(results):
    failed_questions = [r for r in results if not r['correct']]
    if not failed_questions:
        print("No failed questions.")
        return
    
    print(f"{'Question':<50} {'Expected':<30} {'Actual':<30}")
    print("="*110)
    for question in failed_questions:
        statement = question['statement'].split('?')[0] + '?' if '?' in question['statement'] else question['statement']
        statement = statement[:47] + "..." if len(statement) > 47 else statement
        expected = normalize_answer(question['expected'])
        actual = normalize_answer(question['actual'])
        expected = color_text(expected, 'green' if expected == 'yes' else 'red')
        actual = color_text(actual, 'green' if actual == 'yes' else 'red')
        print(f"{statement:<50} {expected:<30} {actual:<30}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the JSON file name as an argument.")
        sys.exit(1)
    
    filename = sys.argv[1]
    results = load_results(filename)
    output_filename = filename.replace('.json', '.png')
    plot_results(results, output_filename)
    
    correct_count = sum(r['correct'] for r in results)
    print(f"Final result: {correct_count}/{len(results)} correct answers")
    
    print_failed_questions(results)
