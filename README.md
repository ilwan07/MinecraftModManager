# Minecraft Mod Manager

![preview](https://cloud-1w4i6hqu7-hack-club-bot.vercel.app/0image.png)

## EN

This app is a modded Minecraft profile manager to organize, update, and share your modded profiles easily, with a simple interface where everything is in one and single place.

### Usage

First, download the app. For Windows, you can use either the installer, or the portable zip version.
For any system, you can directly execute the Python source code, or compile it yourself, just make sure to install the required dependencies. If you do so, use Python 3.12.6 if you have issues.

Once the app is installed, make sure that you have installed the Minecraft Launcher, as this app is not a replacement of the official launcher, but should be installed with it.
Then, make sure to check in the settings that the path to the minecraft data folder is correct, change it if it's not or if you use a custom path.

To use the app, first create a new profile. Give it a name, choose a Minecraft version, and a mod loader. The version and mod loader cannot be changed afterward.
You can click on your profile in the left panel to select it.
You can configure the profile by clicking on the "Configure profile" button. Here, you can rename or delete it.

To install mods, use the search panel on the right: choose a platform to use (from which the mods will be taken), enter a search query, and either hit the enter key, or click the search button. then, click on the mod you want to see or install, select a mod version (use the "(recommended") one or the top one if you're unsure), then hit "Install version"
You can perfectly mix mods from different platforms in your profile, for example install a mod from Modrinth and another mod from Curseforge.

Alternatively, if you can't find the mod you want, you can download it yourself from your browser as a .jar file, then click on the "Add .jar mod" button below your profile name.
You can then choose your .jar file, or multiple ones at the same time if you want, and they will be imported (the .jar mods will always be displayed at the end of the list).
You can remove or rename these mods by clicking on them in the mods panel (second one from the left).

Once a mod is installed, you can remove it or change its version by clicking on it in the mods panel, and then either click "Remove mod", or choose another version and click "Install version".

You can use the "Export" button to export the profile as a .zip file, and then use "Import" to import it back. This file can be shared to someone who's also using this software.

To launch the game, use the "Launch game" button while being on the profile you want to use. This will not affect your previous Minecraft "mods" folder if you already used it before.
If you want to overwrite this folder, use the "Apply profile" button.
Note that the "Launch game" button launches the game in offline mode, meaning that you will be able to play on your local saves, but not on most servers. If you want to play in online mode, then you have to first apply the profile, then use the official Minecraft Launcher (make sure to use the right mod loader and version) to start the game.

### Notable features

- Works on Windows (tested on Win11), should in theory work on Linux and MacOS (use from source)
- Auto language and dark mode
- Ability to change the Minecraft folder in the settings
- Directly launch and play with the "Launch game" button
- Import and export your profiles to make backups or share them with friends
- If you can't find a mod, or want to use your own ones, you can directly install mods from their .jar file
- When creating a profile, choose any Minecraft version you want (including snapshots)
- Choose your mod loader: support for Fabric, Forge, NeoForge and Quilt
- Directly search and download mods from several providers: Modrinth and Curseforge
- Filter versions by compatibility (enabled by default) for the right Minecraft version, and shown versions are always compatible with the mod loader
- By default, your profiles won't overwrite your previous Minecraft mods folder (click "Apply profile" if you want to do it)

### Things to do next

- Authentication to use online mode
- Automatic dependencies installation
- Automatic mod loader installation
- Global optimization

### If you run into any issue

If you run into an issue while using this app, please open an issue on this GitHub repository, explaining what caused the issue, and what you did, also give your latest log file.
The log file can be found in your local app data folder (C:/users/[your username]/AppData/Local for Windows), under Ilwan/MinecraftModManager/logs/latest.log, this will greatly help me resolving the issue.

## FR

Cette application est un gestionnaire de profils Minecraft moddés, pour vous aider à organiser, mettre à jour, et partager vos profils moddés facilement, avec une interface simple où tout se trouve à un seul et unique endroit.

### Utilisation

Tout d'abord, téléchargez l'application. Pour Windows, vous pouvez utiliser soit l'installateur, soit la version portable en zip.
Pour tout système, vous pouvez directement exécuter le code source Python, ou le compiler vous-même, assurez-vous simplement d'installer les dépendances requises. Si vous le faites, utilisez Python 3.12.6 en cas de problèmes.

Une fois l'application installée, assurez-vous d'avoir installé le Launcher Minecraft, car cette application ne remplace pas le launcher officiel, mais doit être installée avec celui-ci.
Ensuite, vérifiez dans les paramètres que le chemin vers le dossier des données de Minecraft est correct, changez-le s'il ne l'est pas ou si vous utilisez un chemin personnalisé.

Pour utiliser l'application, créez d'abord un nouveau profil. Donnez-lui un nom, choisissez une version de Minecraft et un lanceur de mod. La version et le lanceur de mod ne pourront pas être modifiés par la suite. Vous pouvez cliquer sur votre profil dans le panneau de gauche pour le sélectionner.
Vous pouvez configurer le profil en cliquant sur le bouton "Configurer le profil". Ici, vous pouvez le renommer ou le supprimer.

Pour installer des mods, utilisez le panneau de recherche à droite : choisissez une plateforme à utiliser (d'où proviendront les mods), entrez une requête de recherche, puis appuyez sur la touche entrée ou cliquez sur le bouton de recherche. Ensuite, cliquez sur le mod que vous souhaitez voir ou installer, sélectionnez une version du mod (utilisez la version "(recommended)" ou la première si vous n'êtes pas sûr), puis cliquez sur "Installer version".
Vous pouvez parfaitement mélanger des mods de différentes plateformes dans votre profil, par exemple installer un mod depuis Modrinth et un autre mod depuis Curseforge.

Alternativement, si vous ne trouvez pas le mod que vous souhaitez, vous pouvez le télécharger vous-même depuis votre navigateur sous forme de fichier .jar, puis cliquer sur le bouton "Ajouter mod .jar" sous le nom de votre profil.
Vous pouvez ensuite choisir votre fichier .jar, ou plusieurs en même temps si vous le souhaitez, et ils seront importés (les mods .jar seront toujours affichés à la fin de la liste).
Vous pouvez supprimer ou renommer ces mods en cliquant dessus dans le panneau des mods (le deuxième à partir de la gauche).

Une fois un mod installé, vous pouvez le supprimer ou changer sa version en cliquant dessus dans le panneau des mods, puis en cliquant soit sur "Retirer mod", soit en choisissant une autre version et en cliquant sur "Installer version".

Vous pouvez utiliser le bouton "Exporter" pour exporter le profil sous forme de fichier .zip, puis utiliser "Importer" pour le réimporter. Ce fichier peut être partagé avec quelqu'un qui utilise également ce logiciel.

Pour lancer le jeu, utilisez le bouton "Lancer le jeu" tout en étant sur le profil que vous souhaitez utiliser. Cela n'affectera pas votre dossier "mods" Minecraft précédent si vous l'avez déjà utilisé auparavant.
Si vous souhaitez écraser ce dossier, utilisez le bouton "Appliquer le profil".
Notez que le bouton "Lancer le jeu" lance le jeu en mode hors ligne, ce qui signifie que vous pourrez jouer sur vos sauvegardes locales, mais pas sur la plupart des serveurs. Si vous souhaitez jouer en mode en ligne, vous devez d'abord appliquer le profil, puis utiliser le Launcher Minecraft officiel (assurez-vous d'utiliser le bon lanceur de mod et la bonne version) pour démarrer le jeu.

### Fonctionnalités notables

- Fonctionne sur Windows (testé sur Win11), devrait en théorie fonctionner sur Linux et MacOS (utilisation à partir du code source)
- Langue et mode sombre automatiques
- Possibilité de changer le dossier Minecraft dans les paramètres
- Lancer et jouer directement avec le bouton "Lancer le jeu"
- Importer et exporter vos profils pour faire des sauvegardes ou les partager avec des amis
- Si vous ne trouvez pas un mod, ou souhaitez utiliser les vôtres, vous pouvez directement installer des mods à partir de leur fichier .jar
- Lors de la création d'un profil, choisissez n'importe quelle version de Minecraft que vous souhaitez (y compris les snapshots)
- Choisissez votre lanceur de mod : support pour Fabric, Forge, NeoForge et Quilt
- Recherchez et téléchargez directement des mods à partir de plusieurs fournisseurs : Modrinth et Curseforge
- Filtrer les versions par compatibilité (activé par défaut) pour la bonne version de Minecraft, et les versions affichées sont toujours compatibles avec le lanceur de mod
- Par défaut, vos profils n'écraseront pas votre dossier de mods Minecraft précédent (cliquez sur "Appliquer le profil" si vous souhaitez le faire)

### Prochaines étapes

- Authentification pour utiliser le mode en ligne
- Installation automatique des dépendances
- Installation automatique du lanceur de mod
- Optimisation globale

### Si vous rencontrez un problème

Si vous rencontrez un problème lors de l'utilisation de cette application, veuillez ouvrir une "Issue" sur ce dépôt GitHub, en expliquant ce qui a causé le problème et ce que vous avez fait, donnez également votre dernier fichier de log.
Le fichier de log se trouve dans votre dossier de données d'application locale (C:/users/[votre nom d'utilisateur]/AppData/Local pour Windows), sous Ilwan/MinecraftModManager/logs/latest.log, cela m'aidera grandement à résoudre le problème.
