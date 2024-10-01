from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import Job, User

def match_jobs(user_id):
    user = User.query.get(user_id)
    if not user:
        return []

    # Get all jobs from the database
    all_jobs = Job.query.all()
    
    # Filter jobs based on user preferences
    filtered_jobs = [
        job for job in all_jobs
        if (not user.job_title_preference or user.job_title_preference.lower() in job.title.lower()) and
           (not user.job_type_preference or user.job_type_preference.lower() == job.job_type.lower()) and
           (not user.industry_preference or user.industry_preference.lower() == job.industry.lower()) and
           (not user.location_preference or user.location_preference.lower() in job.location.lower()) and
           (not user.salary_min or (job.salary and job.salary >= user.salary_min)) and
           (not user.experience_level or user.experience_level.lower() == job.experience_required.lower())
    ]
    
    if not filtered_jobs:
        return []

    # Create a list of job descriptions
    job_descriptions = [job.description for job in filtered_jobs]
    
    # Get user's resume content
    resume = user.resume[0] if user.resume else None
    if not resume:
        return filtered_jobs  # Return filtered jobs without content matching if no resume

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    
    # Fit and transform job descriptions and resume content
    tfidf_matrix = vectorizer.fit_transform(job_descriptions + [resume.content])
    
    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    
    # Sort jobs by similarity score
    similar_jobs = sorted(zip(filtered_jobs, cosine_similarities[0]), key=lambda x: x[1], reverse=True)
    
    # Return top 10 matching jobs
    return [job for job, score in similar_jobs[:10]]
