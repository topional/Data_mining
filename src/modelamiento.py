"""Preprocesamiento y comparación reproducible del TP1 (semanas 5 y 6)."""

from pathlib import Path
import json
import platform

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score,
    confusion_matrix, f1_score, make_scorer, precision_recall_curve,
    precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import PredefinedSplit, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

SEMILLA = 42
NUMERICAS = ["HORAS_ACADEMICAS", "MES_INICIO", "ANIO_INICIO"]
METRICAS = ["accuracy", "precision", "recall", "f1", "balanced_accuracy", "ap", "roc_auc"]


def cargar_train(root):
    """Leer solo train y comprobar los folds; test se lee después de decidir."""
    carpeta = Path(root) / "data" / "processed"
    train = pd.read_csv(carpeta / "train.csv", encoding="utf-8-sig")
    roles = json.loads((carpeta / "roles_columnas.json").read_text(encoding="utf-8"))
    predictoras = roles["predictoras_candidatas"]
    prohibidas = {"y", "FOLD", "EDICION", "ESTADO_CAPACITACION", "DURACION_DIAS",
                  "TERMINO", "FECHA_TERMINO_CORREGIDA", "HORAS_ATIPICA", "DURACION_ATIPICA"}
    assert not set(predictoras) & prohibidas, "Una predictora contiene información prohibida"
    assert set(train["y"].unique()) == {0, 1}
    assert set(train["FOLD"].unique()) == set(range(5)), "Se esperan los cinco folds del notebook 03"
    assert train.groupby("EDICION")["FOLD"].nunique().eq(1).all()
    assert train.groupby("FOLD")["y"].agg(["min", "max"]).eq([0, 1]).all().all()
    X = train[predictoras].copy()
    y = train["y"].astype(int)
    categorias = [c for c in predictoras if c not in NUMERICAS]
    # Conversión determinista de representación, sin aprender estadísticas.
    X[categorias] = X[categorias].astype(object).where(X[categorias].notna(), np.nan)
    cv = list(PredefinedSplit(train["FOLD"].to_numpy()).split())
    return train, X, y, categorias, cv


def preprocesador(categorias, escalar):
    pasos_num = [("imputar", SimpleImputer(strategy="median", keep_empty_features=True))]
    if escalar:
        pasos_num.append(("escalar", StandardScaler()))
    cat = Pipeline([
        ("imputar", SimpleImputer(strategy="constant", fill_value="SIN_DATO", keep_empty_features=True)),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=True)),
    ])
    return ColumnTransformer([
        ("numericas", Pipeline(pasos_num), NUMERICAS),
        ("categoricas", cat, categorias),
    ], remainder="drop")


def construir_modelos(categorias):
    """Configuraciones preliminares fijadas antes de consultar el test."""
    candidatos = {
        "Dummy mayoritario": (DummyClassifier(strategy="most_frequent"), False),
        "Regresión logística": (LogisticRegression(
            C=1.0, class_weight="balanced", solver="lbfgs", max_iter=2000,
            random_state=SEMILLA), True),
        "Árbol de decisión": (DecisionTreeClassifier(
            max_depth=6, min_samples_leaf=50, class_weight="balanced",
            random_state=SEMILLA), False),
        "Random forest": (RandomForestClassifier(
            n_estimators=150, max_depth=10, min_samples_leaf=20,
            class_weight="balanced_subsample", random_state=SEMILLA,
            n_jobs=2), False),
    }
    return {nombre: Pipeline([("preparar", preprocesador(categorias, escala)),
                              ("clasificar", modelo)])
            for nombre, (modelo, escala) in candidatos.items()}


def metricas(y, prob, umbral=0.5):
    pred = (np.asarray(prob) >= umbral).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "accuracy": float(accuracy_score(y, pred)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y, pred)),
        "ap": float(average_precision_score(y, prob)),
        "roc_auc": float(roc_auc_score(y, prob)),
        "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp),
        "alertas": int(pred.sum()), "umbral": float(umbral),
    }


def comparar_cv(modelos, X, y, cv):
    scoring = {
        "accuracy": "accuracy", "balanced_accuracy": "balanced_accuracy",
        "precision": make_scorer(precision_score, zero_division=0),
        "recall": make_scorer(recall_score, zero_division=0),
        "f1": make_scorer(f1_score, zero_division=0),
        "ap": "average_precision", "roc_auc": "roc_auc",
    }
    filas, probabilidades = [], {}
    for nombre, pipeline in modelos.items():
        print(f"Evaluando {nombre}: cinco folds por edición", flush=True)
        resultado = cross_validate(
            pipeline, X, y, cv=cv, scoring=scoring,
            return_train_score=True, return_estimator=True,
            error_score="raise", n_jobs=1,
        )
        oof = np.full(len(y), np.nan)
        for fold, (estimador, (_, idx_val)) in enumerate(zip(resultado["estimator"], cv)):
            oof[idx_val] = estimador.predict_proba(X.iloc[idx_val])[:, 1]
            fila = {"modelo": nombre, "fold": fold,
                    "segundos_fit": resultado["fit_time"][fold]}
            for m in METRICAS:
                fila[m] = resultado[f"test_{m}"][fold]
                fila[f"train_{m}"] = resultado[f"train_{m}"][fold]
            filas.append(fila)
        assert np.isfinite(oof).all(), "Faltan predicciones de validación"
        probabilidades[nombre] = oof
    detalle = pd.DataFrame(filas)
    resumen = detalle.groupby("modelo", sort=False)[METRICAS].agg(["mean", "std"])
    resumen.columns = [f"{metrica}_{estad}" for metrica, estad in resumen.columns]
    resumen = resumen.join(detalle.groupby("modelo")["train_ap"].mean())
    resumen["brecha_ap"] = resumen["train_ap"] - resumen["ap_mean"]
    resumen = resumen.sort_values(["ap_mean", "ap_std"], ascending=[False, True])
    return detalle, resumen, probabilidades


def seleccionar_umbral(y, prob):
    """Maximizar F1 en OOF; estas métricas son de desarrollo, no una prueba nueva."""
    precision, recall, thresholds = precision_recall_curve(y, prob)
    f1 = np.divide(2 * precision[:-1] * recall[:-1], precision[:-1] + recall[:-1],
                   out=np.zeros_like(thresholds), where=(precision[:-1] + recall[:-1]) > 0)
    tabla = pd.DataFrame({"umbral": thresholds, "precision": precision[:-1],
                          "recall": recall[:-1], "f1": f1})
    # Desempate: más recall; después mayor umbral para un resultado determinista.
    mejor = tabla.sort_values(["f1", "recall", "umbral"], ascending=[False, False, False]).iloc[0]
    return float(mejor["umbral"]), tabla


def evaluar_test(root, train, X, y, modelos, nombre, umbral):
    test = pd.read_csv(Path(root) / "data/processed/test.csv", encoding="utf-8-sig")
    assert set(train["EDICION"]).isdisjoint(set(test["EDICION"]))
    X_test = test[X.columns].copy()
    cats = [c for c in X.columns if c not in NUMERICAS]
    X_test[cats] = X_test[cats].astype(object).where(X_test[cats].notna(), np.nan)
    y_test = test["y"].astype(int)
    final = clone(modelos[nombre]).fit(X, y)
    prob = final.predict_proba(X_test)[:, 1]
    dummy = clone(modelos["Dummy mayoritario"]).fit(X, y)
    prob_dummy = dummy.predict_proba(X_test)[:, 1]
    resultados = pd.DataFrame([
        {"evaluacion": "Dummy mayoritario", **metricas(y_test, prob_dummy)},
        {"evaluacion": f"{nombre} · umbral 0.5", **metricas(y_test, prob)},
        {"evaluacion": f"{nombre} · umbral OOF", **metricas(y_test, prob, umbral)},
    ]).set_index("evaluacion")
    pred = (prob >= umbral).astype(int)
    diagnostico = test[["EDICION", "NOMBRE_CAPACITACION", "SEXO", "NIVEL_GOBIERNO",
                       "TIPO_CAPACITACION", "DEPARTAMENTO", "ESTADO_CAPACITACION", "y"]].copy()
    diagnostico["score_riesgo"] = prob
    diagnostico["prediccion"] = pred
    diagnostico["resultado"] = np.select(
        [(y_test == 1) & (pred == 1), (y_test == 0) & (pred == 1),
         (y_test == 1) & (pred == 0)], ["TP", "FP", "FN"], default="TN")
    segmentos = []
    for columna in ["SEXO", "NIVEL_GOBIERNO", "TIPO_CAPACITACION"]:
        for grupo, sub in diagnostico.groupby(columna):
            tn, fp, fn, tp = confusion_matrix(sub["y"], sub["prediccion"], labels=[0, 1]).ravel()
            segmentos.append({"variable": columna, "grupo": grupo, "n": len(sub),
                              "positivos": int(tp + fn), "tp": int(tp), "fp": int(fp),
                              "fn": int(fn), "tn": int(tn),
                              "recall": tp / (tp + fn) if tp + fn else np.nan,
                              "precision": tp / (tp + fp) if tp + fp else np.nan,
                              "fpr": fp / (fp + tn) if fp + tn else np.nan})
    return final, test, prob, resultados, diagnostico, pd.DataFrame(segmentos)


def guardar_resultados(root, detalle, resumen, oof, train, nombre, umbral,
                       tabla_umbral, modelo, resultados, diagnostico, segmentos):
    root = Path(root)
    destino = root / "reports" / "metrics"
    destino.mkdir(parents=True, exist_ok=True)
    detalle.to_csv(destino / "cv_folds.csv", index=False)
    resumen.to_csv(destino / "cv_resumen.csv")
    tabla_umbral.to_csv(destino / "umbrales_oof.csv", index=False)
    resultados.to_csv(destino / "test_metricas.csv")
    segmentos.to_csv(destino / "test_segmentos.csv", index=False)
    # Predicciones detalladas reproducibles, fuera de git como los demás datos.
    diagnostico.to_csv(root / "data/processed/predicciones_test.csv", index=False)
    oof_df = pd.DataFrame(oof)
    oof_df.insert(0, "y", train["y"])
    oof_df.insert(0, "FOLD", train["FOLD"])
    oof_df.to_csv(root / "data/processed/predicciones_oof.csv", index=False)
    versiones = {"python": platform.python_version(), "scikit-learn": sklearn.__version__,
                 "numpy": np.__version__, "pandas": pd.__version__, "joblib": joblib.__version__}
    config = {
        "modelo": nombre, "umbral": umbral, "criterio_modelo": "mayor AP media de CV por edición",
        "criterio_umbral": "máximo F1 de predicciones OOF de train",
        "advertencia": "Umbral y modelo elegidos con validación: OOF ajustada es desarrollo, no evaluación independiente.",
        "semilla": SEMILLA, "predictoras": list(modelo.feature_names_in_),
        "versiones": versiones,
        "parametros_clasificador": modelo.named_steps["clasificar"].get_params(),
        "calibracion": "No calibrado; class_weight y selección de umbral impiden asumir probabilidades calibradas.",
    }
    (destino / "seleccion.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "models").mkdir(exist_ok=True)
    joblib.dump({"pipeline": modelo, "umbral": umbral, "predictoras": config["predictoras"]},
                root / "models" / "modelo_tp1.joblib")
    return config
