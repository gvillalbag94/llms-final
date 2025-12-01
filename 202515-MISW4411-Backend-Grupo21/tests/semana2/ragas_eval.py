import os, json, argparse

# Añada las métricas que desean evaluar
from ragas.metrics import faithfulness, context_precision, context_recall
from ragas.evaluation import evaluate
from ragas import SingleTurnSample, EvaluationDataset

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI

parser = argparse.ArgumentParser()
parser.add_argument("--ans_exp", type=str, default="")
parser.add_argument("--ans_not_exp", type=str, default="")
parser.add_argument("--ctx_exp", type=str, default="")
parser.add_argument("--ctx_not_exp", type=str, default="")
parser.add_argument("--questions", type=str, default='')
args = parser.parse_args()
ans_exp = args.ans_exp
ans_not_exp = args.ans_not_exp
ctx_exp = json.loads(args.ctx_exp)
ctx_not_exp = json.loads(args.ctx_not_exp)
questions = json.loads(args.questions)

def load_dataset():
    """
    Carga las respuestas generadas durante las pruebas del API para evaluarlas
    """

    evaluation_dataset = []
    for key, value in questions.items():
        question = ''
        if 'question' in value:
            question = value['question']
        answer=''
        context = []
        if key == 'EXPECT_RESPONSE':
            answer=ans_exp
            context = ctx_exp
        elif key == 'DONT_EXPECT_RESPONSE':
            answer=ans_not_exp
            context = ctx_not_exp
        ref_ans = ''
        if 'reference_answer' in value:
            ref_ans = value['reference_answer']
        print(question)
        print(answer)
        print(ref_ans)
        print(context)
        evaluation_dataset.append(SingleTurnSample(
            user_input=question,
            response= answer,
            reference = ref_ans,
            retrieved_contexts = context,
        ))
    return evaluation_dataset

def get_mean(metric):
    def is_valid_number(x):
        # Check if x is a float or int and not NaN or infinite
        return isinstance(x, (int, float)) and not (x != x or x in (float('inf'), float('-inf')))

    # Case 1: single float or int
    if isinstance(metric, (int, float)):
        return metric if is_valid_number(metric) else None

    # Case 2: list or tuple
    if isinstance(metric, (list, tuple)):
        if all(is_valid_number(x) for x in metric) and metric:
            return sum(metric) / len(metric)
        else:
            return None

    # Case 3: invalid type
    return None

def evaluate_rag_with_ragas(dataset):

    """
    Evalúa el sistema RAG utilizando las métricas definidas por RAGAS.
    Imprime información del proceso y retorna los resultados de evaluación.
    """

    # Configura el modelo de lenguaje para evaluación (sin aleatoriedad) y el modelo de embeddings.
    # Se recomienda usar un modelo ligero para la evaluación
    llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash-lite", temperature = 0)
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-002")

    # Lista de métricas RAGAS a utilizar.
    metrics = [faithfulness, context_precision, context_recall]

    print(f"\nEvaluando {len(dataset)} preguntas...")
    print("Procesando métricas RAGAS...")

    # Ejecuta la evaluación con las métricas seleccionadas, utilizando el modelo LLM y embeddings definidos.
    results = evaluate(
            dataset = dataset,
            metrics = metrics,
            llm = llm,
            embeddings = embeddings
    )

    return results

print("\nEVALUACIÓN RAG CON RAGAS")
print("=" * 40)
print("\nCarga de las preguntas y respuestas")
print("--" * 20)
questions = load_dataset()
dataset = EvaluationDataset(samples=questions)
print("\nPreguntas cargadas")
print("--" * 20)
eval_results = evaluate_rag_with_ragas(dataset)

# Extract metric values
faith = eval_results["faithfulness"]
precision = eval_results["context_precision"]
recall = eval_results["context_recall"]

# Print results
print("📊 Resultados de la evalaución con RAGAS:")
print(f"Faithfulness: {faith}")
print(f"Context Precision: {precision}")
print(f"Context Recall: {recall}")

threshold = 0.6
alerts = []



if get_mean(faith) < threshold:
    alerts.append("⚠️ Faithfulness está bajo!")
if get_mean(precision) < threshold:
    alerts.append("⚠️ Context Precision está bajo!")
if get_mean(recall) < threshold:
    alerts.append("⚠️ Context Recall está bajo!")

if alerts:
    print("\n".join(alerts))
else:
    print("✅ Todas las métricas están en un rango aceptable")
