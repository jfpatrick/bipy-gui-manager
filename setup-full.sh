# Color Escapes
NC='\033[0;m'
BOLD='\033[1;m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'

# Actual script
deactivate
clear
echo -e "_________________________________________________________________________"
echo -e "       ___       __   __         ___    ___  __     ___       ___        "
echo -e " |  | |__  |    /    /  \  |\/| |__      |  /  \     |  |__| |__         "
echo -e " |/\| |___ |___ \__  \__/  |  | |___     |  \__/     |  |  | |___        "
echo -e "     ____        ____  __     _       ___                      __        "
echo -e "    / __ \__  __/ __ \/ /_   | |     / (_)___  ____ __________/ /        "
echo -e "   / /_/ / / / / / / / __/   | | /| / / /_  / / __ '/ ___/ __  /         "
echo -e "  / ____/ /_/ / /_/ / /_     | |/ |/ / / / /_/ /_/ / /  / /_/ /          "
echo -e " /_/    \__, /\___\_\__/     |__/|__/_/ /___/\__,_/_/   \__,_/           "
echo -e "       /____/                                                            "
echo -e "_________________________________________________________________________"
echo -e ""
echo -e "Welcome to BI's PyQt5 Project Setup Wizard!"
echo -e "_________________________________________________________________________"
echo -e ""
echo -e "Setup:\n"
while true
do
  echo -ne "${GREEN}=>${NC} Please enter your ${GREEN}project's name${NC}:  "
  read project_name
  if [[ $project_name =~ ^[a-z0-9\-]+$ ]]; then
    break
  else
    echo -e "${RED}=> Error!${YELLOW} The project name can contain only letters, numbers and dashes${NC}"
  fi
done

while true
do
  echo -ne "${GREEN}=>${NC} Please enter a ${GREEN}one-line description${NC} of your project:  "
  read project_desc
  if [[ $project_desc =~ ^.*[\"].*$ ]]; then
    echo -e "${RED}=> Error!${YELLOW} The project description cannot contain the character \" ${NC}"
  else
    break
  fi
done

while true
do
  echo -ne "${GREEN}=>${NC} Please enter the project's ${GREEN}author name${NC}:  "
  read project_author
  if [[ $project_author =~ ^.*[\"].*$ ]]; then
    echo -e "${RED}=> Error!${YELLOW} The name cannot contain the character \" ${NC}"
  else
    break
  fi
done

while true
do
  echo -ne "${GREEN}=>${NC} And the author's ${GREEN}CERN email address${NC}:  "
  read project_email
  if [[ "${project_email}" =~ [a-zA-Z0-9._%+-]+@cern\.ch ]]; then
    echo -e "${RED}=> Error! ${YELLOW}Invalid CERN email, try again${NC}"
  else
    break
  fi
done

echo -e "_________________________________________________________________________"
echo -e ""
echo -e "Installation:"


# Checkout template code
echo -e "${GREEN}=>${NC} Downloading template from GitLab...  "
git config core.askPass ""
git_success=$(git clone https://gitlab.cern.ch/szanzott/be-bi-pyqt-template.git template >/dev/null 2>&1)
while ! $git_success
do
  echo -ne "${RED}=>${YELLOW} Failed to clone the template! Do you want to retry? (yes/no)${NC}  "
  read answer
  if [[ $answer == "no" ]]; then
    exit 1
  fi
done
# Temporary debugging replacement
#mkdir wizard
#cp -r ../be-bi-pyqt-template/!(venv) wizard
#rm -rf wizard/*.egg-info
echo -e "   ${GREEN}Done${NC}"

# Generate various project names variations
project_name_underscores="${project_name//-/_}"
project_name_spaces="${project_name//-/ }"
project_name_capitals=$(sed -e "s/\b\(.\)/\u\1/g" <<< $project_name_spaces)

# Rename tree root
echo -e "${GREEN}=>${NC} Creating project under $project_name/...  "
mv template/be_bi_pyqt_template template/$project_name_underscores
mv template $project_name
rm -r $project_name/images
rm $project_name/install.sh
echo -e "   ${GREEN}Done${NC}"

# Replace strings into files
echo -e "${GREEN}=>${NC} Applying customizations...  "
grep -rl "be-bi-pyqt-template" . | xargs sed -i "s/be-bi-pyqt-template/${project_name}/g"
grep -rl "be_bi_pyqt_template" . | xargs sed -i "s/be_bi_pyqt_template/${project_name_underscores}/g"
grep -rl "BE BI PyQt Template Code" . | xargs sed -i "s/BE BI PyQt Template Code/${project_desc}/g"
grep -rl "BE BI PyQt Template" . | xargs sed -i "s/BE BI PyQt Template/${project_name_capitals}/g"
grep -rl "Sara Zanzottera" . | xargs sed -i "s/Sara Zanzottera/${project_author}/g"
grep -rl "sara.zanzottera@cern.ch" . | xargs sed -i "s/sara.zanzottera@cern.ch/${project_email}/g"
echo -e "   ${GREEN}Done${NC}"

# Write out README
echo -e "${GREEN}=>${NC} Preparing README...  "
cd $project_name
rm README.md
mv README-template.md README.md
sed -i "s/Project Name/${project_name_capitals}/g" README.md
sed -i "s/_Here goes the project description_/${project_desc}/g" README.md
sed -i "s/project-name/${project_name}/g" README.md
echo "    - Hint: check the README for typos, as it was auto-generated"
echo -e "   ${GREEN}Done${NC}"

# Setup venvs
echo -e "${GREEN}=>${NC} Activating virtualenvs... "
source /acc/local/share/python/acc-py-pyqt/install.sh  >/dev/null 2>&1
acc-py venv venv  >/dev/null 2>&1
source venv/bin/activate
echo -e "   ${GREEN}Done${NC}"

# Install with pip
echo -e "${GREEN}=>${NC} Installing the project...  "
if pip install -e . -qqqq; then

  # Success!
  echo -e "   ${GREEN}Done${NC}"
  echo -e "${GREEN}_________________________________________________________________________${NC}\n"
  echo -e "${GREEN}=>${NC} New project installed successfully!"
  echo -e "${GREEN}=>${NC} Please make sure all went well by typing '$project_name' in the console"
  echo -e "${GREEN}_________________________________________________________________________${NC}\n"
  echo -e "${GREEN}=>${NC} - Hint: type 'pyqt-manager --help' to see more workflows."
  # remove yourself
  rm ../install.sh

else

  # Failure
  echo -e "   ${RED}Fail!${NC}"
  echo -e "${RED}_________________________________________________________________________${NC}\n"
  echo -e "${RED}=> Error!${YELLOW} New project failed to install ${NC}"
  echo -e "Please execute ${YELLOW}pip install -e $project_name${NC} and, if it fails, send the log to the maintainers."
  echo -e "${RED}_________________________________________________________________________${NC}\n"

fi

# Go back to the dir we started from
cd ../