from be_bi_pyqt_project_manager import cli_utils as cli


def create_project():
    print("_________________________________________________________________________\n")
    print("  Welcome to BI's PyQt5 Project Setup Wizard!                            ")
    print("_________________________________________________________________________\n")
    print("  Setup:\n")
    project_name = input(cli.positive_feedback("Please enter your \033[0;32mproject's name\033[0;m:"))
        # Validate echo -e "${RED}=> Error!${YELLOW} The project name can contain only letters, numbers and dashes${NC}"
    project_desc = input(cli.positive_feedback("Please enter a \033[0;32mone-line description\033[0;m of your project:"))
        # Validate "${RED}=> Error!${YELLOW} The project description cannot contain the character \" ${NC}"
    project_authon = input(cli.positive_feedback("Please enter the project's \033[0;32mauthor name\033[0;m:"))
        # Validate echo -e "${RED}=> Error!${YELLOW} The name cannot contain the character \" ${NC}"
    author_email = input(cli.positive_feedback("Please enter the author's \033[0;32mCERN email address\033[0;m:"))
        # Validate "${RED}=> Error! ${YELLOW}Invalid CERN email, try again${NC}"

    print("_________________________________________________________________________\n")
    print("  Installation:\n")

    print(cli.positive_feedback("Downloading template from GitLab..."))
        # Do it
        # Failed to clone the template! Do you want to retry? (yes/no)
    print(cli.success_feedback())

    print(cli.positive_feedback("Creating project under {}/...".format(project_name)))
    # Do it
    print(cli.success_feedback())

    print(cli.positive_feedback("Applying customizations..."))
    # Do it
    print(cli.success_feedback())

    print(cli.positive_feedback("Preparing README..."))

    print(cli.give_hint("check the README for typos, as it was auto-generated"))
    # Do it
    print(cli.success_feedback())

    print(cli.positive_feedback("Activating virtualenvs..."))
    # Do it
    print(cli.success_feedback())

    print(cli.positive_feedback("Installing the project..."))
    # Do it
    print(cli.success_feedback())

    print(cli.positive_feedback("Preparing README..."))
    # Do it
    print(cli.success_feedback())

