from itertools import islice

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from faker import Faker

from core.models import Profile
from questions.models import Answer, AnswerLike, Question, QuestionLike, Tag


BATCH_SIZE = 5000


def batched(items, size):
    iterator = iter(items)
    while batch := list(islice(iterator, size)):
        yield batch


class Command(BaseCommand):
    help = 'Fill database with generated test data.'

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int)

    def handle(self, *args, **options):
        ratio = options['ratio']
        if ratio <= 0:
            raise CommandError('ratio must be a positive integer')

        fake = Faker('ru_RU')
        batch_key = timezone.now().strftime('%Y%m%d%H%M%S')

        users_count = ratio
        tags_count = ratio
        questions_count = ratio * 10
        answers_count = ratio * 100
        likes_count = ratio * 200
        max_likes_count = users_count * (questions_count + answers_count)
        if likes_count > max_likes_count:
            raise CommandError(
                f'Cannot create {likes_count} unique likes for ratio={ratio}. '
                f'Maximum is {max_likes_count}.'
            )

        self.stdout.write('Creating users...')
        users = User.objects.bulk_create(
            [
                User(
                    username=f'user_{batch_key}_{i}',
                    email=f'user_{batch_key}_{i}@example.com',
                    password='!',
                )
                for i in range(users_count)
            ],
            batch_size=BATCH_SIZE,
        )
        Profile.objects.bulk_create(
            [Profile(user=user) for user in users],
            batch_size=BATCH_SIZE,
        )

        self.stdout.write('Creating tags...')
        tag_question_counts = [0] * tags_count
        for i in range(questions_count):
            tag_question_counts[i % tags_count] += 1
            tag_question_counts[(i * 7 + 1) % tags_count] += 1

        tags = Tag.objects.bulk_create(
            [
                Tag(name=f'{fake.word()}_{batch_key}_{i}', questions_count=tag_question_counts[i])
                for i in range(tags_count)
            ],
            batch_size=BATCH_SIZE,
        )

        self.stdout.write('Creating questions...')
        question_answer_counts = [0] * questions_count
        for i in range(answers_count):
            question_answer_counts[i % questions_count] += 1

        questions = Question.objects.bulk_create(
            [
                Question(
                    author=users[i % users_count],
                    title=fake.sentence(nb_words=8),
                    text=fake.paragraph(nb_sentences=4),
                    rating=fake.random_int(min=0, max=500),
                    answers_count=question_answer_counts[i],
                )
                for i in range(questions_count)
            ],
            batch_size=BATCH_SIZE,
        )

        self.stdout.write('Linking questions and tags...')
        through_model = Question.tags.through
        tag_links = (
            through_model(question_id=question.id, tag_id=tag_id)
            for i, question in enumerate(questions)
            for tag_id in (
                tags[i % tags_count].id,
                tags[(i * 7 + 1) % tags_count].id,
            )
        )
        for batch in batched(tag_links, BATCH_SIZE):
            through_model.objects.bulk_create(batch, batch_size=BATCH_SIZE, ignore_conflicts=True)

        self.stdout.write('Creating answers...')
        answer_ids = []
        for start in range(0, answers_count, BATCH_SIZE):
            batch = [
                Answer(
                    question=questions[i % questions_count],
                    author=users[(i * 13 + 3) % users_count],
                    text=fake.paragraph(nb_sentences=5),
                    is_correct=(i % 23 == 0),
                    rating=fake.random_int(min=0, max=300),
                )
                for i in range(start, min(start + BATCH_SIZE, answers_count))
            ]
            answer_ids.extend(
                answer.id for answer in Answer.objects.bulk_create(batch, batch_size=BATCH_SIZE)
            )

        question_ids = [question.id for question in questions]
        user_ids = [user.id for user in users]

        question_likes_count = min(likes_count // 2, questions_count * users_count)
        answer_likes_count = likes_count - question_likes_count
        if answer_likes_count > answers_count * users_count:
            raise CommandError('Cannot create enough unique answer likes.')

        self.stdout.write('Creating question likes...')
        question_likes = (
            QuestionLike(
                question_id=question_ids[i % questions_count],
                user_id=user_ids[i // questions_count],
                value=1,
            )
            for i in range(question_likes_count)
        )
        for batch in batched(question_likes, BATCH_SIZE):
            QuestionLike.objects.bulk_create(batch, batch_size=BATCH_SIZE, ignore_conflicts=True)

        self.stdout.write('Creating answer likes...')
        answer_likes = (
            AnswerLike(
                answer_id=answer_ids[i % answers_count],
                user_id=user_ids[i // answers_count],
                value=1,
            )
            for i in range(answer_likes_count)
        )
        for batch in batched(answer_likes, BATCH_SIZE):
            AnswerLike.objects.bulk_create(batch, batch_size=BATCH_SIZE, ignore_conflicts=True)

        self.stdout.write(
            self.style.SUCCESS(
                f'Created {users_count} users, {questions_count} questions, '
                f'{answers_count} answers, {tags_count} tags and {likes_count} likes.'
            )
        )
