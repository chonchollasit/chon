from routines import RemyRoutine, AdamsRoutine


def main():
    for routine_cls in [RemyRoutine, AdamsRoutine]:
        routine = routine_cls()
        routine.run()


if __name__ == "__main__":
    main()
