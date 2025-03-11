# Documentació del Sistema de Predicció de Chollos en Portàtils

## Introducció

Aquest document explica el procés de desenvolupament d'un model de predicció per a identificar "chollos" (ofertes excel·lents) en el mercat de portàtils. El sistema analitza les especificacions tècniques i preus dels dispositius per a determinar quins representen una millor relació qualitat-preu.

## Conjunt de Dades

El conjunt de dades utilitzat (`specs_simplified_all.csv`) conté informació detallada sobre diversos models de portàtils, incloent:

- Processador
- Memòria RAM
- Tipus de RAM (DDR4, DDR5, etc.)
- Emmagatzematge
- Targeta gràfica
- Mida de pantalla
- Resolució
- Sistema operatiu
- Capacitat de la bateria
- Preu

## Procés d'Anàlisi i Predicció

### 1. Preprocessament de Dades

```python
# Càrrega de les dades
df_original = pd.read_csv(file_path, sep=',')
df = df_original.copy()

# Preprocessament del preu
df['Precio'] = df['Precio'].str.replace('.', '').str.replace(',', '.').astype(float)

# Gestió de valors nuls
df['RAM'] = df['RAM'].fillna(8)
df['Almacenamiento'] = df['Almacenamiento'].fillna(512)
df['Bateria'] = df['Bateria'].fillna(df['Bateria'].median())
```

El preprocessament inclou:
- Neteja del format dels preus (canvi de format europeu a format numèric)
- Ompliment de valors nuls en les columnes importants
- Creació de noves característiques derivades

### 2. Enginyeria de Característiques

S'han creat diverses característiques noves per a millorar el model:

#### Identificació del Tipus de Processador

```python
# Creació d'una columna per al tipus de processador
df['Tipo'] = df['Procesador'].apply(lambda x: 'Intel' if 'Intel' in str(x) else 
                                   ('Apple' if 'Apple' in str(x) else 
                                   ('AMD' if 'AMD' in str(x) else 
                                   ('Qualcomm' if 'Qualcomm' in str(x) else 'Otro'))))
```

#### Extracció de la Generació de CPU

```python
# Funció per extraure la generació de CPU d'Intel
def extract_cpu_gen(cpu):
    if not isinstance(cpu, str):
        return 0
    if 'Core i' in cpu:
        for i in range(3, 15):  # Generacions Intel 3-14
            if f'i{i}-' in cpu or f'i{i} ' in cpu:
                return i
    elif 'Ultra' in cpu:
        return 15  # Ultra és la més nova
    elif 'M' in cpu:
        return int(cpu.split('-')[1][1]) if '-M' in cpu else 0
    return 0
```

#### Conversió de Resolució a Píxels

```python
# Funció per convertir la resolució a píxels totals
def extract_resolution_pixels(res_str):
    if not isinstance(res_str, str):
        return 0
    try:
        parts = res_str.split('x')
        if len(parts) == 2:
            return int(parts[0]) * int(parts[1])
        return 0
    except:
        return 0
```

#### Quantificació del Tipus de RAM

```python
# Convertir 'Tipus RAM' a un valor numèric (generació DDR)
def ram_type_to_num(ram_type):
    if not isinstance(ram_type, str):
        return 4  # Per defecte DDR4 si falta
    try:
        if 'DDR' in ram_type:
            return int(ram_type.replace('DDR', ''))
        return 4  # Per defecte DDR4 si no s'especifica
    except:
        return 4
```

#### Puntuació de Qualitat i Valor

```python
# Crear una puntuació de qualitat basada en les especificacions
df['Quality_Score'] = (
    df['RAM'] * 0.3 +
    df['Almacenamiento'] * 0.2 +
    df['Bateria'] * 0.1 +
    df['CPU_Generation'] * 50
)

# Calcular una puntuació de valor (qualitat per preu)
df['Value_Score'] = df['Quality_Score'] / df['Precio']
```

### 3. Etiquetatge de Dades per a Entrenament

Per a entrenar el model, es van etiquetar automàticament algunes dades basant-se en el valor de Value_Score:

```python
# Etiquetatge basat en el llindar de valor
high_value_threshold = df['Value_Score'].quantile(0.75)
low_value_threshold = df['Value_Score'].quantile(0.25)

# Etiquetar puntuacions altes com "chollo" (1) i baixes com "no chollo" (0)
high_value_sample = df[df['Value_Score'] > high_value_threshold].sample(min(30, len(df[df['Value_Score'] > high_value_threshold])))
low_value_sample = df[df['Value_Score'] < low_value_threshold].sample(min(30, len(df[df['Value_Score'] < low_value_threshold])))

high_value_sample['es_chollo'] = 1  # Chollo
low_value_sample['es_chollo'] = 0   # No chollo
```

També es van aplicar correccions manuals basades en coneixement específic del domini:

```python
# Ajustar dispositius Apple cars (normalment no es consideren "chollos")
if 'Apple' in str(row['Procesador']) and row['Precio'] > 1500:
    labeled_data.at[idx, 'es_chollo'] = 0

# Portàtils econòmics amb bones especificacions solen ser bones ofertes
if row['Precio'] < 500 and row['RAM'] >= 8 and row['Almacenamiento'] >= 512:
    labeled_data.at[idx, 'es_chollo'] = 1
```

### 4. Preparació de Característiques per al Model

```python
# Convertir dades categòriques a codificació one-hot
categorical_columns = ['Tipo', 'Sistema Operativo', 'Graficos']
labeled_data_encoded = pd.get_dummies(labeled_data, columns=categorical_columns, dummy_na=True)
```

### 5. Entrenament del Model

S'ha utilitzat un model de Random Forest per a la classificació:

```python
# Dividir les dades en conjunts d'entrenament i prova
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Escalar les característiques
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Entrenar un model Random Forest
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)
```

### 6. Avaluació del Model

L'avaluació del model inclou:
- Precisió global
- Informe de classificació (precisió, recall, f1-score)
- Importància de les característiques

```python
# Avaluar el model
y_pred = model.predict(X_test_scaled)
print("Model Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Obtenir importància de les característiques
feature_importance = pd.DataFrame({
    'Feature': all_features,
    'Importance': model.feature_importances_
})
```

### 7. Predicció en el Conjunt de Dades Complet

```python
# Predir en el conjunt de dades complet
chollo_predictions = model.predict(X_full_scaled)
chollo_probabilities = model.predict_proba(X_full_scaled)[:, 1]

# Afegir prediccions al dataframe original
df_original['Chollo'] = chollo_predictions
df_original['Probabilidad_Chollo'] = chollo_probabilities
```

### 8. Anàlisi de Resultats i Visualitzacions

El sistema genera diverses visualitzacions per a entendre millor les prediccions:

- **Importància de característiques:** Mostra quins factors són més determinants per a identificar chollos
- **Distribució de preus:** Compara la distribució de preus entre chollos i no-chollos
- **RAM vs Preu:** Visualitza la relació entre RAM i preu, amb color segons la classificació
- **Emmagatzematge vs Preu:** Visualitza la relació entre capacitat d'emmagatzematge i preu

## Factors Determinants per a Identificar Chollos

El model considera múltiples factors per a determinar si un portàtil és un "chollo", incloent:

1. **Value_Score:** La relació entre qualitat i preu
2. **Preu:** Portàtils amb preus més baixos del que s'esperaria per les seues especificacions
3. **RAM i Emmagatzematge:** Portàtils amb més memòria del normal per al seu rang de preu
4. **Generació del processador:** Tecnologia més recent a preus raonables
5. **Tipus de RAM:** DDR5 es valora més que DDR4 a preus similars
6. **Resolució de pantalla:** Més píxels a preus competitius

## Resultats i Conclusions

El model aconsegueix identificar portàtils que presenten una excel·lent relació qualitat-preu segons les seues especificacions. Els resultats es guarden en el fitxer `chollos.csv`, que conté totes les columnes originals més la classificació binària "Chollo" (1 = és chollo, 0 = no és chollo) i la columna "Probabilidad_Chollo" que indica la confiança del model en aquesta classificació.

Els "chollos" identificats tendeixen a ser:

1. Portàtils amb especificacions d'alta gamma a preus de gamma mitjana
2. Equips econòmics amb especificacions sorprenentment bones
3. Models amb característiques equilibrades i preus competitius

## Limitacions i Millores Futures

- **Dades temporals:** Els preus i les especificacions canvien amb el temps, cal actualitzar regularment el model.
- **Aspectes qualitatius:** No es consideren factors com la qualitat de construcció, teclat o pantalla.
- **Marca i reputació:** No s'han incorporat factors de marca o servei postvenda.
- **Disponibilitat:** No es considera si el producte està disponible o no.

En futures versions es podria incorporar:
- Anàlisi de sentiment de ressenyes d'usuaris
- Històric de preus per a detectar ofertes temporals
- Comparació amb models similars del mateix fabricant
- Més detalls tècnics com tipus de panell, taxa de refresc, etc.

## Ús i Interpretació

El fitxer `chollos.csv` pot ser utilitzat per a:

1. Identificar ràpidament les millors ofertes del mercat
2. Comparar productes similars i entendre per què alguns representen millor valor
3. Prendre decisions de compra informades basades en dades objectives

Les columnes més rellevants per a l'usuari final són:
- **Chollo:** Indica si és una bona oferta (1) o no (0)
- **Probabilidad_Chollo:** Indica la confiança del model en aquesta classificació (0-1)

## Recursos i Referències

- Scikit-learn: https://scikit-learn.org/
- Pandas: https://pandas.pydata.org/
- Seaborn: https://seaborn.pydata.org/
- Matplotlib: https://matplotlib.org/