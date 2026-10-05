"""Comprobaciones de comportamiento del pipeline, sin depender del CSV real."""

import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.modelamiento import construir_modelos, metricas, seleccionar_umbral


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.X = pd.DataFrame({
            "HORAS_ACADEMICAS": [2., 4., 6., 8., np.nan, 10.],
            "MES_INICIO": [1, 1, 2, 2, 3, 3], "ANIO_INICIO": [2025] * 6,
            "MODALIDAD": ["REMOTA", "PRESENCIAL"] * 3,
        })
        self.y = [0, 1, 0, 1, 0, 1]

    def test_nuevas_categorias_y_faltantes_no_reajustan_preparacion(self):
        pipeline = construir_modelos(["MODALIDAD"])["Regresión logística"].fit(self.X, self.y)
        prep = pipeline.named_steps["preparar"]
        mediana = prep.named_transformers_["numericas"].named_steps["imputar"].statistics_.copy()
        categorias = prep.named_transformers_["categoricas"].named_steps["onehot"].categories_[0].copy()
        nuevo = self.X.iloc[:2].copy()
        nuevo["MODALIDAD"] = ["NUEVA", np.nan]
        nuevo["HORAS_ACADEMICAS"] = [10000., np.nan]
        pred = pipeline.predict_proba(nuevo)
        self.assertEqual(pred.shape, (2, 2))
        self.assertTrue(np.isfinite(pred).all())
        np.testing.assert_array_equal(mediana, prep.named_transformers_["numericas"].named_steps["imputar"].statistics_)
        np.testing.assert_array_equal(categorias, prep.named_transformers_["categoricas"].named_steps["onehot"].categories_[0])

    def test_errores_y_umbral_tienen_sentido(self):
        y = np.array([0, 0, 1, 1])
        prob = np.array([0.1, 0.7, 0.3, 0.8])
        m = metricas(y, prob, 0.5)
        self.assertEqual((m["tn"], m["fp"], m["fn"], m["tp"]), (1, 1, 1, 1))
        self.assertEqual(m["precision"], 0.5)
        self.assertEqual(m["recall"], 0.5)
        t, _ = seleccionar_umbral(y, prob)
        self.assertAlmostEqual(t, 0.3)
        self.assertAlmostEqual(metricas(y, prob, t)["f1"], 0.8)

    def test_ap_depende_del_ranking_y_no_del_umbral(self):
        y = np.array([0, 0, 1, 1])
        p = np.array([0.1, 0.7, 0.3, 0.8])
        self.assertEqual(metricas(y, p, 0.2)["ap"], metricas(y, p, 0.9)["ap"])
        self.assertEqual(metricas(y, np.zeros(4))["ap"], 0.5)


if __name__ == "__main__":
    unittest.main()
