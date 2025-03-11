import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns

# Load the CSV data
file_path = 'specs_simplified_all.csv'
df_original = pd.read_csv(file_path, sep=',')

# Create a working copy to preserve the original structure
df = df_original.copy()

# Data preprocessing
df['Precio'] = df['Precio'].str.replace('.', '').str.replace(',', '.').astype(float)

# Handle missing values
df['RAM'] = df['RAM'].fillna(8)
df['Almacenamiento'] = df['Almacenamiento'].fillna(512)
df['Bateria'] = df['Bateria'].fillna(df['Bateria'].median())

# Create a column for "Tipo" (CPU type) based on Procesador
df['Tipo'] = df['Procesador'].apply(lambda x: 'Intel' if 'Intel' in str(x) else 
                                        ('Apple' if 'Apple' in str(x) else 
                                         ('AMD' if 'AMD' in str(x) else 
                                          ('Qualcomm' if 'Qualcomm' in str(x) else 'Otro'))))

# Extract more features
def extract_cpu_gen(cpu):
    if not isinstance(cpu, str):
        return 0
    if 'Core i' in cpu:
        for i in range(3, 15):  # Intel generations 3-14
            if f'i{i}-' in cpu or f'i{i} ' in cpu:
                return i
    elif 'Ultra' in cpu:
        return 15  # Ultra is newest
    elif 'M' in cpu:
        return int(cpu.split('-')[1][1]) if '-M' in cpu else 0
    return 0

# Apply the function to create a new column
df['CPU_Generation'] = df['Procesador'].apply(extract_cpu_gen)

# Create a quality score based on specs
df['Quality_Score'] = (
    df['RAM'] * 0.3 +
    df['Almacenamiento'] * 0.2 +
    df['Bateria'] * 0.1 +
    df['CPU_Generation'] * 50
)

# Calculate a value score (quality per price)
df['Value_Score'] = df['Quality_Score'] / df['Precio']

# Manually labeled examples (based on good value for the specs)
# Higher value score could indicate a better deal
high_value_threshold = df['Value_Score'].quantile(0.75)
low_value_threshold = df['Value_Score'].quantile(0.25)

# Create a subset of labeled data for training
labeled_data = pd.DataFrame()

# Labeling high value scores as "chollo" (1) and low value scores as "no chollo" (0)
high_value_sample = df[df['Value_Score'] > high_value_threshold].sample(min(30, len(df[df['Value_Score'] > high_value_threshold])))
low_value_sample = df[df['Value_Score'] < low_value_threshold].sample(min(30, len(df[df['Value_Score'] < low_value_threshold])))

high_value_sample['es_chollo'] = 1  # Chollo
low_value_sample['es_chollo'] = 0   # No chollo

# Combine the labeled samples
labeled_data = pd.concat([high_value_sample, low_value_sample])

# Some manual corrections based on domain knowledge
# For example, very cheap laptops with decent specs or high-end laptops at good prices
for idx, row in labeled_data.iterrows():
    # Adjust expensive Apple devices (they're typically not considered "chollos" unless significantly discounted)
    if 'Apple' in str(row['Procesador']) and row['Precio'] > 1500:
        labeled_data.at[idx, 'es_chollo'] = 0
    
    # Budget laptops with good specs are often good deals
    if row['Precio'] < 500 and row['RAM'] >= 8 and row['Almacenamiento'] >= 512:
        labeled_data.at[idx, 'es_chollo'] = 1
    
    # Laptops with high-end CPUs at moderate prices are good deals
    if 'i7' in str(row['Procesador']) and row['Precio'] < 900 and row['RAM'] >= 16:
        labeled_data.at[idx, 'es_chollo'] = 1

# Process categorical columns and prepare features for the model
# Function to convert screen resolution to numeric pixels
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

# Create more advanced features
labeled_data['Resolution_Pixels'] = labeled_data['Resolucion'].apply(extract_resolution_pixels)
df['Resolution_Pixels'] = df['Resolucion'].apply(extract_resolution_pixels)

# Convert 'Tipo RAM' to a numeric value (DDR generation)
def ram_type_to_num(ram_type):
    if not isinstance(ram_type, str):
        return 4  # Default to DDR4 if missing
    try:
        if 'DDR' in ram_type:
            return int(ram_type.replace('DDR', ''))
        return 4  # Default to DDR4 if not specified
    except:
        return 4

labeled_data['RAM_Type_Num'] = labeled_data['Tipo RAM'].apply(ram_type_to_num)
df['RAM_Type_Num'] = df['Tipo RAM'].apply(ram_type_to_num)

# Screen size to float
def screen_size_to_float(size):
    if not isinstance(size, (int, float, str)):
        return 15.6  # Default value
    try:
        if isinstance(size, str):
            return float(size)
        return size
    except:
        return 15.6

labeled_data['Screen_Size_Num'] = labeled_data['Pantalla'].apply(screen_size_to_float)
df['Screen_Size_Num'] = df['Pantalla'].apply(screen_size_to_float)

# Prepare a more comprehensive feature list
numerical_features = [
    'RAM', 'Almacenamiento', 'Bateria', 'Precio', 
    'CPU_Generation', 'Quality_Score', 'Value_Score',
    'Resolution_Pixels', 'RAM_Type_Num', 'Screen_Size_Num'
]

# Check which features exist in our dataset
valid_features = [col for col in numerical_features if col in labeled_data.columns]

# Convert categorical data to one-hot encoding for training
categorical_columns = ['Tipo', 'Sistema Operativo', 'Graficos']
labeled_data_encoded = pd.get_dummies(labeled_data, columns=categorical_columns, dummy_na=True)
df_encoded = pd.get_dummies(df, columns=categorical_columns, dummy_na=True)

# Identify all dummy columns created
dummy_features = [col for col in labeled_data_encoded.columns 
                  if any(col.startswith(cat + '_') for cat in categorical_columns)]

# Combine numerical and dummy features
all_features = valid_features + dummy_features
all_features = [col for col in all_features if col in labeled_data_encoded.columns and col != 'es_chollo']

# Split the labeled data into training and testing sets
X = labeled_data_encoded[all_features]
y = labeled_data_encoded['es_chollo']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Train a Random Forest model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate the model
y_pred = model.predict(X_test_scaled)
print("Model Accuracy:", accuracy_score(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Get feature importance
feature_importance = pd.DataFrame({
    'Feature': all_features,
    'Importance': model.feature_importances_
})
feature_importance = feature_importance.sort_values('Importance', ascending=False)
print("\nFeature Importance:")
print(feature_importance.head(10))  # Show top 10 most important features

# Plot feature importance
plt.figure(figsize=(10, 6))
top_features = feature_importance.head(10)
sns.barplot(x='Importance', y='Feature', data=top_features)
plt.title('Top 10 Feature Importance for "Chollo" Classification')
plt.tight_layout()
plt.savefig('feature_importance.png')

# Ensure all columns in X are present in the full dataset for prediction
for col in X.columns:
    if col not in df_encoded.columns:
        df_encoded[col] = 0

# Get the same columns as the training set
X_full = df_encoded[all_features]

# Scale the features
X_full_scaled = scaler.transform(X_full)

# Predict on the full dataset
chollo_predictions = model.predict(X_full_scaled)
chollo_probabilities = model.predict_proba(X_full_scaled)[:, 1]

# Add predictions to the original dataframe
df_original['Precio'] = df['Precio']  # Use the processed price values
df_original['Chollo'] = chollo_predictions
df_original['Probabilidad_Chollo'] = chollo_probabilities

# Save the complete dataset with the "Chollo" column
df_original.to_csv('chollos.csv', index=False)

# Show the top 10 "chollos" with highest probability
print("\nTop 10 'Chollos' encontrados:")
top_chollos = df_original[df_original['Chollo'] == 1].sort_values('Probabilidad_Chollo', ascending=False).head(10)
print(top_chollos[['Procesador', 'RAM', 'Almacenamiento', 'Precio', 'Chollo', 'Probabilidad_Chollo']])

# Visualize price distribution by chollo classification
plt.figure(figsize=(10, 6))
sns.histplot(data=df_original, x='Precio', hue='Chollo', bins=30, kde=True)
plt.title('Distribución de Precios por Clasificación de Chollo')
plt.xlabel('Precio (€)')
plt.tight_layout()
plt.savefig('price_distribution.png')

# Visualize the relationship between RAM and Price, colored by chollo classification
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_original, x='RAM', y='Precio', hue='Chollo', alpha=0.7)
plt.title('RAM vs Precio por Clasificación de Chollo')
plt.xlabel('RAM (GB)')
plt.ylabel('Precio (€)')
plt.tight_layout()
plt.savefig('ram_vs_price.png')

# Visualize the relationship between Storage and Price, colored by chollo classification
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_original, x='Almacenamiento', y='Precio', hue='Chollo', alpha=0.7)
plt.title('Almacenamiento vs Precio por Clasificación de Chollo')
plt.xlabel('Almacenamiento (GB)')
plt.ylabel('Precio (€)')
plt.tight_layout()
plt.savefig('storage_vs_price.png')

print("\nAnálisis completo. Resultados guardados en 'chollos.csv'")
print("Este archivo contiene todas las columnas originales más las columnas 'Chollo' y 'Probabilidad_Chollo'")
print("Visualizaciones guardadas como 'feature_importance.png', 'price_distribution.png', 'ram_vs_price.png', y 'storage_vs_price.png'")
