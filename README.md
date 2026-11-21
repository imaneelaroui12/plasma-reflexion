# GSR1 — Réflexion d'une onde sur un plasma

Petite application web Streamlit pour le mini-projet d'Imane Elaroui (enseignant : El Mamouni). Elle montre comment la température, la densité de référence, la fréquence, l'angle et la polarisation modifient la réflexion sur un plasma idéal.

Le plasma est homogène, non magnétisé, sans collisions et semi-infini. Le schéma des particules et la représentation de l'onde sont illustratifs.

## Lancement

Python 3.10 ou plus récent est recommandé. Ouvrir un terminal dans ce dossier, puis lancer :

    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    streamlit run app.py

Sous Windows, activer l'environnement avec :

    .venv\Scripts\activate

L'application s'ouvre dans un navigateur. « Lecture » et « Pause » animent le schéma; « Réinitialiser » remet les réglages de départ.

## Commandes

- Température commune du plasma, de 300 à 3000 K.
- Fréquence de l'onde, de 0,5 à 10 GHz.
- Angle d'incidence de 0 à 80 degrés, mesuré par rapport à la normale.
- Densité électronique de référence réglable sur une échelle logarithmique.
- Polarisation TE ou TM.

La température de référence est fixée à T₀ = 300 K. La densité du plasma évolue selon :

    Ne(T) = Ne0 × T0 / T

La fréquence plasma et la permittivité sont calculées par :

    omega_p = sqrt(Ne × e² / (epsilon0 × me))
    fp = omega_p / (2 pi)
    epsilon_r = 1 − (omega_p / omega)²

## Propagation, Fresnel et puissance

Le nombre normal d'onde relatif vaut :

    q² = epsilon_r − sin²(theta_i)

Si q² > 0, le champ transmis est propagatif. Sinon, il est évanescent. Le seuil dépend donc de l'angle :

    f > fp / cos(theta_i)

Pour le calcul des coefficients, l'application prend :

    TE: Gamma = (cos(theta_i) − q) / (cos(theta_i) + q)
        t     = 2 cos(theta_i) / (cos(theta_i) + q)

    TM: Gamma = (epsilon_r cos(theta_i) − q) / (epsilon_r cos(theta_i) + q)
        t     = 2 sqrt(epsilon_r) cos(theta_i) /
                (epsilon_r cos(theta_i) + q)

Pour une onde propagative, R = |Gamma|² et la puissance transmise est :

    T = (q / cos(theta_i)) × |t|²

Le facteur q/cos(theta_i) convertit le rapport d'amplitudes en rapport de flux de puissance. Dans le cas évanescent, un champ décroissant existe dans le plasma, mais son flux moyen normal est nul; l'application affiche R = 100 % et T = 0 %. Dans le modèle sans pertes et sans face arrière, R + T vaut 100 % à l'arrondi numérique près.

## Références des constantes

Les constantes e, epsilon0, me et c sont les valeurs recommandées du CODATA/NIST :

- [NIST — constantes fondamentales](https://physics.nist.gov/cuu/Constants/)
- [NIST — rapport CODATA 2022](https://physics.nist.gov/cuu/pdf/JPCRD2022CODATA.pdf)

## Limites

Le modèle n'est pas une simulation complète de l'ionosphère. Il ne tient pas compte des collisions, d'un champ magnétique, des variations spatiales de densité, d'une température différente entre espèces, ni d'une seconde interface. Les particules du schéma ne sont pas à l'échelle réelle.
