from routines import RemyRoutine, AdamsRoutine, JKRoutine


def main():
    for routine_cls in [RemyRoutine, AdamsRoutine, JKRoutine]:
        routine = routine_cls()
        routine.run()


if __name__ == "__main__":
    main()
