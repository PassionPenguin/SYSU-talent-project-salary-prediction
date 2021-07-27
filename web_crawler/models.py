class Job:
    # Job Model
    # def __init__(self, title, published_at, salary, address, basic_requirement, need, company, company_information,
    #              company_category, tags, description):
    #     self.title = title
    #     self.published_at = published_at
    #     self.salary = salary
    #     self.address = address
    #     self.basic_requirement = basic_requirement
    #     self.need = need
    #     self.company = company
    #     self.company_information = company_information
    #     self.company_category = company_category
    #     self.tags = tags
    #     self.description = description
    def __init__(self, url, title, area, salary, company_type, requirements, company_name, description=""):
        self.url = url
        self.title = title
        self.area = area
        self.salary = salary
        self.company_type = company_type
        self.requirements = requirements
        self.company_name = company_name
        self.description = description