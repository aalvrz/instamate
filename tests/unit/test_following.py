from instamate.following import FollowParameters


class TestFollowParameters:
    def test_passing_parameters(self):
        parameters = FollowParameters(
            min_posts_count=150, min_followers=500, min_followings=1000
        )
        assert parameters.should_follow(234, 700, 1200)

        parameters = FollowParameters(min_followers=500, min_followings=1000)
        assert parameters.should_follow(2, 505, 1020)

    def test_unpassing_parameters(self):
        parameters = FollowParameters(
            min_posts_count=10, min_followers=100, min_followings=100
        )
        assert not parameters.should_follow(0, 200, 1000)

        parameters = FollowParameters(
            min_posts_count=10, min_followers=100, min_followings=100
        )
        assert not parameters.should_follow(20, 200, 5)
